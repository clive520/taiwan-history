// 《島嶼鐵道物語》前端互動主程式 (Project IronVeins)
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
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  // 2. 初始化分期分類標籤
  renderPeriodTabs();

  // 3. 初始渲染視圖
  renderViews();

  // 4. 事件監聽
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim().toLowerCase();
      if (clearSearch) clearSearch.classList.toggle('hidden', currentSearch === '');
      renderViews();
    });
  }

  if (clearSearch) {
    clearSearch.addEventListener('click', () => {
      searchInput.value = '';
      currentSearch = '';
      clearSearch.classList.add('hidden');
      renderViews();
    });
  }

  // 視角切換事件
  if (viewGridBtn) viewGridBtn.addEventListener('click', () => switchView('grid'));
  if (viewTimelineBtn) viewTimelineBtn.addEventListener('click', () => switchView('timeline'));
  if (viewMapBtn) viewMapBtn.addEventListener('click', () => switchView('map'));
  if (mobileViewGridBtn) mobileViewGridBtn.addEventListener('click', () => switchView('grid'));
  if (mobileViewTimelineBtn) mobileViewTimelineBtn.addEventListener('click', () => switchView('timeline'));
  if (mobileViewMapBtn) mobileViewMapBtn.addEventListener('click', () => switchView('map'));

  function switchView(view) {
    currentView = view;

    // 更新 Desktop 按鈕樣式
    const activeClass = ['bg-white', 'dark:bg-slate-900', 'text-indigo-900', 'dark:text-indigo-200', 'shadow-sm', 'font-semibold'];
    const inactiveClass = ['text-slate-600', 'dark:text-slate-400', 'hover:text-indigo-800', 'dark:hover:text-white'];

    [viewGridBtn, viewTimelineBtn, viewMapBtn].forEach(btn => {
      if (!btn) return;
      btn.classList.remove(...activeClass);
      btn.classList.add(...inactiveClass);
    });

    if (view === 'grid' && viewGridBtn) viewGridBtn.classList.add(...activeClass);
    if (view === 'timeline' && viewTimelineBtn) viewTimelineBtn.classList.add(...activeClass);
    if (view === 'map' && viewMapBtn) viewMapBtn.classList.add(...activeClass);

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
    if (typeof TAIWAN_RAILWAY_DATA === 'undefined') return [];
    return TAIWAN_RAILWAY_DATA.filter(item => {
      const matchPeriod = currentPeriod === 'all' || item.period === currentPeriod;
      const matchSearch = currentSearch === '' || 
        item.title.toLowerCase().includes(currentSearch) ||
        item.subtitle.toLowerCase().includes(currentSearch) ||
        item.summary.toLowerCase().includes(currentSearch) ||
        (item.figures && item.figures.some(f => f.toLowerCase().includes(currentSearch))) ||
        (item.coordinates && item.coordinates.locationName.toLowerCase().includes(currentSearch));
      return matchPeriod && matchSearch;
    });
  }

  // 渲染所有視圖內容
  function renderViews() {
    const filtered = getFilteredChapters();
    if (resultsCount) {
      resultsCount.textContent = `共收錄 ${filtered.length} 個百年鐵道紀事專題`;
    }
    if (emptyState) {
      emptyState.classList.toggle('hidden', filtered.length > 0);
    }

    renderGrid(filtered);
    renderTimeline(filtered);
    if (currentView === 'map') {
      updateMapMarkers(filtered);
    }

    if (window.lucide) {
      lucide.createIcons();
    }
  }

  // 渲染卡片目錄
  function renderGrid(chapters) {
    if (!chaptersGrid) return;

    chaptersGrid.innerHTML = chapters.map(item => {
      const isPublished = item.status === 'published';
      const statusBadge = isPublished 
        ? `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">已上線</span>`
        : `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-300 dark:border-indigo-800">特輯進行中</span>`;

      // 代表圖騰 / 技術標籤
      const figureChips = (item.figures || []).slice(0, 4).map(fig => 
        `<span class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-indigo-50 dark:bg-indigo-950/40 text-indigo-800 dark:text-indigo-300 border border-indigo-200/50 dark:border-indigo-800/40">#${fig}</span>`
      ).join(' ');

      const linkUrl = `article.html?series=railway&id=${item.id}`;

      // 封面圖片或預設鐵道漸層
      const coverHtml = item.bannerImage 
        ? `<div class="h-44 w-full overflow-hidden relative"><img src="${item.bannerImage}" alt="${item.title}" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'h-44 w-full bg-gradient-to-tr from-slate-900 via-indigo-950 to-blue-900 flex flex-col items-center justify-center text-indigo-300/70\\'><i data-lucide=\\'train\\' class=\\'w-12 h-12 mb-2\\'></i><span class=\\'text-xs tracking-wider font-mono\\'>IRONVEINS</span></div>'; lucide.createIcons();"></div>`
        : `<div class="h-44 w-full bg-gradient-to-tr from-slate-900 via-indigo-950 to-blue-900 flex flex-col items-center justify-center text-indigo-300/70">
             <i data-lucide="train" class="w-12 h-12 mb-2"></i>
             <span class="text-xs tracking-wider font-mono">IRONVEINS</span>
           </div>`;

      return `
        <a href="${linkUrl}" class="group railway-card rounded-2xl bg-white dark:bg-slate-900 border border-indigo-200/70 dark:border-slate-800/80 overflow-hidden flex flex-col justify-between shadow-sm hover:shadow-md hover:border-indigo-400 dark:hover:border-indigo-700 transition-all">
          <div>
            ${coverHtml}
            <div class="p-5">
              <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-2">
                <span class="font-semibold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                  <span>第 ${item.chapterNo} 章</span>
                  <span>&bull;</span>
                  <span class="truncate max-w-[130px]">${item.periodName.split('：')[1] || item.periodName}</span>
                </span>
                ${statusBadge}
              </div>
              <h3 class="text-base font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors mb-1 line-clamp-1">
                ${item.title}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-2.5 line-clamp-1 font-medium">
                ${item.subtitle}
              </p>
              
              <!-- 技術與文化圖騰標籤 -->
              <div class="flex flex-wrap gap-1.5 mb-3">
                ${figureChips}
              </div>

              <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-2">
                ${item.summary}
              </p>
            </div>
          </div>
          <div class="px-5 py-3 border-t border-indigo-100 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 bg-indigo-50/30 dark:bg-slate-900/50">
            <span class="flex items-center gap-1 truncate max-w-[200px]">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-indigo-500 shrink-0"></i>
              <span class="truncate">${item.coordinates ? item.coordinates.locationName : '全島鐵道'}</span>
            </span>
            <span class="text-indigo-600 dark:text-indigo-400 font-semibold group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
              啟程 <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            </span>
          </div>
        </a>
      `;
    }).join('');
  }

  // 渲染時間軸
  function renderTimeline(chapters) {
    if (!timelineList) return;

    timelineList.innerHTML = chapters.map((item, index) => {
      const isEven = index % 2 === 0;
      const linkUrl = `article.html?series=railway&id=${item.id}`;

      return `
        <div class="relative flex flex-col md:flex-row items-center ${isEven ? 'md:flex-row-reverse' : ''}">
          <div class="w-full md:w-1/2 ${isEven ? 'md:pl-8' : 'md:pr-8'} pl-10 md:pl-0">
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-indigo-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
              <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 mb-2">
                ${item.era}
              </span>
              <h4 class="text-base font-bold text-slate-900 dark:text-white mb-1">
                第 ${item.chapterNo} 章：${item.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">${item.subtitle}</p>
              <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-3">${item.summary}</p>
              
              <div class="flex items-center justify-between pt-2 border-t border-indigo-100 dark:border-slate-800 text-xs">
                <span class="text-slate-400 flex items-center gap-1">
                  <i data-lucide="map-pin" class="w-3 h-3 text-indigo-500"></i>
                  ${item.coordinates ? item.coordinates.locationName : '全島'}
                </span>
                <a href="${linkUrl}" class="inline-flex items-center font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
                  深入閱讀 <i data-lucide="arrow-right" class="w-3 h-3 ml-1"></i>
                </a>
              </div>
            </div>
          </div>
          <!-- 節點錨點 -->
          <div class="absolute left-4 md:left-1/2 w-4 h-4 rounded-full bg-indigo-600 border-2 border-white dark:border-slate-950 shadow-sm transform -translate-x-1/2"></div>
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
        fillColor: '#4f46e5',
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.95
      }).addTo(mapInstance);

      const linkUrl = `article.html?series=railway&id=${item.id}`;
      const figures = (item.figures || []).map(f => `<span class="inline-block bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 text-[10px] px-1.5 py-0.2 rounded mr-1 mb-1">#${f}</span>`).join('');

      const popupHtml = `
        <div class="p-1 min-w-[200px]">
          <div class="text-xs font-semibold text-indigo-600 mb-1">第 ${item.chapterNo} 章 &bull; ${item.era}</div>
          <div class="text-sm font-bold text-slate-900 mb-1">${item.title}</div>
          <div class="text-xs text-slate-500 mb-2">${item.coordinates.locationName}</div>
          <div class="mb-2">${figures}</div>
          <p class="text-xs text-slate-700 line-clamp-2 mb-2">${item.summary}</p>
          <a href="${linkUrl}" class="inline-block px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-semibold transition-colors">閱讀本專題</a>
        </div>
      `;

      marker.bindPopup(popupHtml);
      mapMarkers.push(marker);
    });
  }

  // 渲染分期分類 Tab
  function renderPeriodTabs() {
    if (!periodTabs || typeof RAILWAY_PERIODS_DATA === 'undefined') return;

    periodTabs.innerHTML = RAILWAY_PERIODS_DATA.map(p => `
      <button data-period="${p.id}" class="period-tab px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
        p.id === currentPeriod 
          ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/25' 
          : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:bg-indigo-50 dark:hover:bg-slate-800 border border-indigo-200/80 dark:border-slate-800'
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
