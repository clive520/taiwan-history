// 臺灣史文庫前端互動主程式
document.addEventListener('DOMContentLoaded', () => {
  // DOM 元素快取
  const gridSection = document.getElementById('gridSection');
  const timelineSection = document.getElementById('timelineSection');
  const mapSection = document.getElementById('mapSection');
  const chaptersGrid = document.getElementById('chaptersGrid');
  const timelineList = document.getElementById('timelineList');
  const periodTabs = document.getElementById('periodTabs');
  const searchInput = document.getElementById('searchInput');
  const clearSearch = document.getElementById('clearSearch');
  const resultsCount = document.getElementById('resultsCount');
  const emptyState = document.getElementById('emptyState');
  const themeToggle = document.getElementById('themeToggle');

  // 視角切換按鈕
  const viewGridBtn = document.getElementById('viewGridBtn');
  const viewTimelineBtn = document.getElementById('viewTimelineBtn');
  const viewMapBtn = document.getElementById('viewMapBtn');
  const mobileViewGridBtn = document.getElementById('mobileViewGridBtn');
  const mobileViewTimelineBtn = document.getElementById('mobileViewTimelineBtn');
  const mobileViewMapBtn = document.getElementById('mobileViewMapBtn');

  // 狀態管理
  let currentPeriod = 'all';
  let currentSearch = '';
  let currentView = 'grid'; // 'grid' | 'timeline' | 'map'
  let mapInstance = null;
  let mapMarkers = [];

  // 1. 初始化深淺主題
  initTheme();
  themeToggle.addEventListener('click', toggleTheme);

  // 2. 初始化時期分類標籤
  renderPeriodTabs();

  // 3. 初始渲染視圖
  renderViews();

  // 4. 事件監聽
  searchInput.addEventListener('input', (e) => {
    currentSearch = e.target.value.trim().toLowerCase();
    clearSearch.classList.toggle('hidden', currentSearch === '');
    renderViews();
  });

  clearSearch.addEventListener('click', () => {
    searchInput.value = '';
    currentSearch = '';
    clearSearch.classList.add('hidden');
    renderViews();
  });

  // 視角切換事件
  viewGridBtn.addEventListener('click', () => switchView('grid'));
  viewTimelineBtn.addEventListener('click', () => switchView('timeline'));
  viewMapBtn.addEventListener('click', () => switchView('map'));
  mobileViewGridBtn.addEventListener('click', () => switchView('grid'));
  mobileViewTimelineBtn.addEventListener('click', () => switchView('timeline'));
  mobileViewMapBtn.addEventListener('click', () => switchView('map'));

  function switchView(view) {
    currentView = view;

    // 更新 Desktop 按鈕樣式
    const activeClass = ['bg-white', 'dark:bg-slate-900', 'text-slate-900', 'dark:text-white', 'shadow-sm'];
    const inactiveClass = ['text-slate-600', 'dark:text-slate-400', 'hover:text-slate-900', 'dark:hover:text-white'];

    [viewGridBtn, viewTimelineBtn, viewMapBtn].forEach(btn => {
      btn.classList.remove(...activeClass);
      btn.classList.add(...inactiveClass);
    });

    if (view === 'grid') viewGridBtn.classList.add(...activeClass);
    if (view === 'timeline') viewTimelineBtn.classList.add(...activeClass);
    if (view === 'map') viewMapBtn.classList.add(...activeClass);

    // 切換區塊顯示
    gridSection.classList.toggle('hidden', view !== 'grid');
    timelineSection.classList.toggle('hidden', view !== 'timeline');
    mapSection.classList.toggle('hidden', view !== 'map');

    if (view === 'map') {
      setTimeout(() => initOrUpdateMap(), 150);
    }
  }

  // 篩選章節資料
  function getFilteredChapters() {
    return TAIWAN_HISTORY_DATA.filter(item => {
      const matchPeriod = currentPeriod === 'all' || item.period === currentPeriod;
      const matchSearch = currentSearch === '' || 
        item.title.toLowerCase().includes(currentSearch) ||
        item.subtitle.toLowerCase().includes(currentSearch) ||
        item.summary.toLowerCase().includes(currentSearch) ||
        item.figures.some(f => f.toLowerCase().includes(currentSearch)) ||
        (item.coordinates && item.coordinates.locationName.toLowerCase().includes(currentSearch));
      return matchPeriod && matchSearch;
    });
  }

  // 渲染所有視圖內容
  function renderViews() {
    const filtered = getFilteredChapters();
    resultsCount.textContent = `共收錄 ${filtered.length} 個歷史專題章節`;
    emptyState.classList.toggle('hidden', filtered.length > 0);

    renderGrid(filtered);
    renderTimeline(filtered);
    if (currentView === 'map') {
      updateMapMarkers(filtered);
    }

    lucide.createIcons();
  }

  // 渲染卡片目錄
  function renderGrid(chapters) {
    chaptersGrid.innerHTML = chapters.map(item => {
      const isPublished = item.status === 'published';
      const statusBadge = isPublished 
        ? `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">已上線</span>`
        : `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700">籌備中</span>`;

      const coverImg = item.bannerImage 
        ? `<div class="h-44 w-full overflow-hidden relative"><img src="${item.bannerImage}" alt="${item.title}" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"></div>`
        : `<div class="h-28 w-full bg-gradient-to-tr from-emerald-100 to-teal-50 dark:from-slate-800 dark:to-slate-900 flex items-center justify-center text-emerald-600/40 dark:text-emerald-400/20"><i data-lucide="book-open" class="w-10 h-10"></i></div>`;

      const linkUrl = isPublished 
        ? `article.html?file=${encodeURIComponent(item.periodFolder + '/' + item.file)}`
        : `javascript:void(0)`;

      return `
        <a href="${linkUrl}" class="group topic-card rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 overflow-hidden flex flex-col justify-between ${!isPublished ? 'opacity-85' : ''}">
          <div>
            ${coverImg}
            <div class="p-5">
              <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-2">
                <span class="font-semibold text-emerald-600 dark:text-emerald-400">第 ${item.chapterNo} 章 &bull; ${item.periodName.split('：')[1]}</span>
                ${statusBadge}
              </div>
              <h3 class="text-base font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors mb-1 line-clamp-1">
                ${item.title}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-3 line-clamp-1 font-medium">
                ${item.subtitle}
              </p>
              <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-4">
                ${item.summary}
              </p>
            </div>
          </div>
          <div class="px-5 py-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-900/50">
            <span class="flex items-center gap-1 truncate max-w-[200px]">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i>
              <span class="truncate">${item.coordinates ? item.coordinates.locationName : '全島'}</span>
            </span>
            <span class="text-emerald-600 dark:text-emerald-400 font-semibold group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
              閱讀 <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            </span>
          </div>
        </a>
      `;
    }).join('');
  }

  // 渲染時間軸
  function renderTimeline(chapters) {
    timelineList.innerHTML = chapters.map((item, index) => {
      const isEven = index % 2 === 0;
      const isPublished = item.status === 'published';
      const linkUrl = isPublished 
        ? `article.html?file=${encodeURIComponent(item.periodFolder + '/' + item.file)}`
        : `javascript:void(0)`;

      return `
        <div class="relative flex flex-col md:flex-row items-center ${isEven ? 'md:flex-row-reverse' : ''}">
          <div class="w-full md:w-1/2 ${isEven ? 'md:pl-8' : 'md:pr-8'} pl-10 md:pl-0">
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
              <span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 mb-2">
                ${item.era}
              </span>
              <h4 class="text-base font-bold text-slate-900 dark:text-white mb-1">
                第 ${item.chapterNo} 章：${item.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">${item.subtitle}</p>
              <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-3">${item.summary}</p>
              <a href="${linkUrl}" class="inline-flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
                深入探索 <i data-lucide="arrow-right" class="w-3 h-3 ml-1"></i>
              </a>
            </div>
          </div>
          <!-- 節點錨點 -->
          <div class="absolute left-4 md:left-1/2 w-4 h-4 rounded-full bg-emerald-500 border-2 border-white dark:border-slate-950 timeline-dot transform -translate-x-1/2"></div>
        </div>
      `;
    }).join('');
  }

  // 初始化與更新 Leaflet 地圖
  function initOrUpdateMap() {
    if (!mapInstance) {
      mapInstance = L.map('mapContainer', {
        center: [23.7, 120.95],
        zoom: 7.5,
        minZoom: 6,
        maxZoom: 12
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(mapInstance);
    }

    updateMapMarkers(getFilteredChapters());
  }

  function updateMapMarkers(chapters) {
    if (!mapInstance) return;

    // 清空舊標記
    mapMarkers.forEach(m => mapInstance.removeLayer(m));
    mapMarkers = [];

    chapters.forEach(item => {
      if (!item.coordinates || !item.coordinates.lat || !item.coordinates.lng) return;

      const marker = L.circleMarker([item.coordinates.lat, item.coordinates.lng], {
        radius: 8,
        fillColor: '#10b981',
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(mapInstance);

      const linkUrl = item.status === 'published'
        ? `article.html?file=${encodeURIComponent(item.periodFolder + '/' + item.file)}`
        : `javascript:void(0)`;

      const popupHtml = `
        <div class="p-1">
          <div class="text-xs font-semibold text-emerald-600 mb-1">第 ${item.chapterNo} 章 &bull; ${item.era}</div>
          <div class="text-sm font-bold text-slate-900 mb-1">${item.title}</div>
          <div class="text-xs text-slate-500 mb-2">${item.coordinates.locationName}</div>
          <p class="text-xs text-slate-700 line-clamp-2 mb-2">${item.summary}</p>
          <a href="${linkUrl}" class="inline-block px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-semibold">閱讀本專題</a>
        </div>
      `;

      marker.bindPopup(popupHtml);
      mapMarkers.push(marker);
    });
  }

  // 渲染時期分類 Tab
  function renderPeriodTabs() {
    periodTabs.innerHTML = PERIODS_DATA.map(p => `
      <button data-period="${p.id}" class="period-tab px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
        p.id === currentPeriod 
          ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-500/20' 
          : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800'
      }">
        ${p.name}
      </button>
    `).join('');

    periodTabs.querySelectorAll('.period-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        currentPeriod = btn.dataset.period;
        renderPeriodTabs();
        renderViews();
      });
    });
  }

  // 深淺模式切換
  function initTheme() {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.theme = isDark ? 'dark' : 'light';
  }
});
