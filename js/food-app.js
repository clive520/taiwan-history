// 《舌尖上的臺灣》前端互動主程式
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

  // 2. 初始化時期分類標籤
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
    const activeClass = ['bg-white', 'dark:bg-slate-900', 'text-amber-900', 'dark:text-amber-200', 'shadow-sm', 'font-semibold'];
    const inactiveClass = ['text-slate-600', 'dark:text-slate-400', 'hover:text-amber-800', 'dark:hover:text-white'];

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
    if (typeof TAIWAN_FOOD_DATA === 'undefined') return [];
    return TAIWAN_FOOD_DATA.filter(item => {
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
      resultsCount.textContent = `共收錄 ${filtered.length} 個臺灣風味飲食專題`;
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
        : `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-800">特輯連載中</span>`;

      // 食材標籤
      const ingredientChips = (item.figures || []).slice(0, 4).map(ing => 
        `<span class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border border-amber-200/50 dark:border-amber-800/40">#${ing}</span>`
      ).join(' ');

      const linkUrl = `article.html?series=food&id=${item.id}`;

      // 封面圖片或預設風土漸層
      const coverHtml = item.bannerImage 
        ? `<div class="h-44 w-full overflow-hidden relative"><img src="${item.bannerImage}" alt="${item.title}" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"></div>`
        : `<div class="h-28 w-full bg-gradient-to-tr from-amber-500/20 via-orange-400/15 to-amber-200/20 dark:from-amber-950/40 dark:to-orange-950/30 flex items-center justify-center text-amber-600/50 dark:text-amber-400/30">
             <i data-lucide="utensils" class="w-10 h-10"></i>
           </div>`;

      return `
        <a href="${linkUrl}" class="group food-card rounded-2xl bg-white dark:bg-slate-900 border border-amber-200/70 dark:border-slate-800/80 overflow-hidden flex flex-col justify-between shadow-sm">
          <div>
            ${coverHtml}
            <div class="p-5">
              <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-2">
                <span class="font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1">
                  <span>第 ${item.chapterNo} 章</span>
                  <span>&bull;</span>
                  <span class="truncate max-w-[130px]">${item.periodName.split('：')[1] || item.periodName}</span>
                </span>
                ${statusBadge}
              </div>
              <h3 class="text-base font-bold text-slate-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors mb-1 line-clamp-1">
                ${item.title}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-2.5 line-clamp-1 font-medium">
                ${item.subtitle}
              </p>
              
              <!-- 食材標籤 -->
              <div class="flex flex-wrap gap-1.5 mb-3">
                ${ingredientChips}
              </div>

              <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-2">
                ${item.summary}
              </p>
            </div>
          </div>
          <div class="px-5 py-3 border-t border-amber-100 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 bg-amber-50/30 dark:bg-slate-900/50">
            <span class="flex items-center gap-1 truncate max-w-[200px]">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-amber-500 shrink-0"></i>
              <span class="truncate">${item.coordinates ? item.coordinates.locationName : '全島風土'}</span>
            </span>
            <span class="text-amber-600 dark:text-amber-400 font-semibold group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
              閱讀 <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
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
      const linkUrl = `article.html?series=food&id=${item.id}`;

      return `
        <div class="relative flex flex-col md:flex-row items-center ${isEven ? 'md:flex-row-reverse' : ''}">
          <div class="w-full md:w-1/2 ${isEven ? 'md:pl-8' : 'md:pr-8'} pl-10 md:pl-0">
            <div class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-amber-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
              <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 mb-2">
                ${item.era}
              </span>
              <h4 class="text-base font-bold text-slate-900 dark:text-white mb-1">
                第 ${item.chapterNo} 章：${item.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">${item.subtitle}</p>
              <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-3">${item.summary}</p>
              
              <div class="flex items-center justify-between pt-2 border-t border-amber-100 dark:border-slate-800 text-xs">
                <span class="text-slate-400 flex items-center gap-1">
                  <i data-lucide="map-pin" class="w-3 h-3 text-amber-500"></i>
                  ${item.coordinates ? item.coordinates.locationName : '全臺'}
                </span>
                <a href="${linkUrl}" class="inline-flex items-center font-semibold text-amber-600 dark:text-amber-400 hover:underline">
                  深入品味 <i data-lucide="arrow-right" class="w-3 h-3 ml-1"></i>
                </a>
              </div>
            </div>
          </div>
          <!-- 節點錨點 -->
          <div class="absolute left-4 md:left-1/2 w-4 h-4 rounded-full bg-amber-500 border-2 border-white dark:border-slate-950 shadow-sm transform -translate-x-1/2"></div>
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
        fillColor: '#d97706',
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.95
      }).addTo(mapInstance);

      const linkUrl = `article.html?series=food&id=${item.id}`;
      const ingredients = (item.figures || []).map(f => `<span class="inline-block bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.2 rounded mr-1 mb-1">#${f}</span>`).join('');

      const popupHtml = `
        <div class="p-1 min-w-[200px]">
          <div class="text-xs font-semibold text-amber-600 mb-1">第 ${item.chapterNo} 章 &bull; ${item.era}</div>
          <div class="text-sm font-bold text-slate-900 mb-1">${item.title}</div>
          <div class="text-xs text-slate-500 mb-2">${item.coordinates.locationName}</div>
          <div class="mb-2">${ingredients}</div>
          <p class="text-xs text-slate-700 line-clamp-2 mb-2">${item.summary}</p>
          <a href="${linkUrl}" class="inline-block px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-xs font-semibold transition-colors">品味本專題</a>
        </div>
      `;

      marker.bindPopup(popupHtml);
      mapMarkers.push(marker);
    });
  }

  // 渲染時期分類 Tab
  function renderPeriodTabs() {
    if (!periodTabs || typeof FOOD_PERIODS_DATA === 'undefined') return;

    periodTabs.innerHTML = FOOD_PERIODS_DATA.map(p => `
      <button data-period="${p.id}" class="period-tab px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
        p.id === currentPeriod 
          ? 'bg-amber-600 text-white shadow-sm shadow-amber-500/25' 
          : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:bg-amber-50 dark:hover:bg-slate-800 border border-amber-200/80 dark:border-slate-800'
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
