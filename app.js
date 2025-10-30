document.addEventListener('DOMContentLoaded', () => {
  const landingScreen = document.getElementById('landing-screen');
  const dashboardScreen = document.getElementById('dashboard-screen');
  const footer = document.getElementById('dashboard-footer');
  const districtSelect = document.getElementById('district-select');
  const metricsContainer = document.getElementById('metrics-container');
  const dataDate = document.getElementById('data-date');
  const districtName = document.querySelector('.district-name');

  // ---------------- Populate District Dropdown ----------------
  // keep a map of districts by id for later lookups
  const districtsMap = {};
  fetch('/api/districts')
    .then(res => res.json())
    .then(data => {
      data.forEach(d => {
        districtsMap[d.id] = d;
        const opt = document.createElement('option');
        // store id (numeric) as the value so backend endpoints that need id work
        opt.value = d.id;
        opt.textContent = d.name;
        districtSelect.appendChild(opt);
      });
    })
    .catch(() => {
      const opt = document.createElement('option');
      opt.textContent = 'ડેટા મળ્યો નથી';
      opt.disabled = true;
      districtSelect.appendChild(opt);
    });

  // ---------------- Manual District Selection ----------------
  document.getElementById('manual-select-btn').addEventListener('click', () => {
    const districtCode = districtSelect.value;
    if (!districtCode) return alert('કૃપા કરીને જિલ્લો પસંદ કરો');
    loadDashboard(districtCode);
  });

  // ---------------- Use Location ----------------
  document.getElementById('use-location-btn').addEventListener('click', () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(pos => {
        const { latitude, longitude } = pos.coords;
        // backend endpoint uses hyphen: /api/nearest-district
        fetch(`/api/nearest-district?lat=${latitude}&lon=${longitude}`)
          .then(res => res.json())
          .then(d => {
            if (!d || !d.id) return alert('નજીકનું જિલ્લું મળ્યું નથી');
            loadDashboard(d.id);
          })
          .catch(() => alert('નજીકનું જિલ્લું મેળવવામાં ત્રુટિ'));
      }, () => alert('સ્થાન મેળવવામાં અસમર્થ'));
    } else {
      alert('સ્થાન મેળવવામાં અસમર્થ');
    }
  });

  // ---------------- Load Dashboard ----------------
  function loadDashboard(districtId) {
    landingScreen.classList.remove('active');
    dashboardScreen.classList.add('active');
    footer.classList.add('show');

    // fetch latest, trend and compare in parallel from the backend
    const latestP = fetch(`/api/district/${districtId}/latest`).then(r => r.json());
    const trendP = fetch(`/api/district/${districtId}/trend`).then(r => r.json());
    const compareP = fetch(`/api/district/${districtId}/compare`).then(r => r.json());

    Promise.all([latestP, trendP, compareP])
      .then(([latest, trendRows, compare]) => {
        const d = districtsMap[districtId] || {};
        districtName.textContent = d.name || (compare && compare.district ? `જિલ્લો` : 'જિલ્લો');
        dataDate.textContent = latest ? `ડેટા: ${latest.month} ${latest.year}` : '';

        // metrics: transform latest into expected array of {label,value,status}
        const metrics = [
          { label: 'રોજગાર દિવસો', value: latest ? latest.person_days : '—', status: '' },
          { label: 'લાભાર્થીઓ', value: latest ? latest.beneficiaries : '—', status: '' },
          { label: 'સરેરાશ મજૂરી', value: latest ? `₹${latest.avg_wage}` : '—', status: '' }
        ];
        renderMetrics(metrics);

        // trend: trendRows is an array of {year,month,person_days}
        const months = (trendRows || []).map(r => `${r.month}/${r.year}`);
        const values = (trendRows || []).map(r => r.person_days);
        renderTrend({ months, values });

        // compare: backend returns district and state_avg_person_days
        renderCompare({ district: compare && compare.district ? `આ જિલ્લો (${compare.district.person_days})` : 'જિલ્લો', days: compare ? compare.state_avg_person_days : 0, wage: compare && compare.district ? compare.district.avg_wage : 0 });
      })
      .catch((err) => {
        console.error(err);
        metricsContainer.innerHTML = `<p>ડેટા ઉપલબ્ધ નથી.</p>`;
      });
  }

  // ---------------- Render Metrics ----------------
  function renderMetrics(metrics) {
    metricsContainer.innerHTML = '';
    metrics.forEach(m => {
      const card = document.createElement('div');
      card.className = 'metric-card';
      card.innerHTML = `
        <div>
          <p class="metric-label">${m.label}</p>
          <p class="metric-value">${m.value}</p>
        </div>
        <div>${m.status}</div>
      `;
      metricsContainer.appendChild(card);
    });
  }

  // ---------------- Trend Chart ----------------
  function renderTrend(trend) {
    const ctx = document.getElementById('trend-chart');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: trend.months,
        datasets: [{
          label: 'રોજગાર દિવસો',
          data: trend.values,
          borderColor: '#16A34A',
          tension: 0.3,
          fill: false
        }]
      }
    });
  }

  // ---------------- Comparison ----------------
  function renderCompare(compare) {
    const container = document.getElementById('compare-container');
    container.innerHTML = `
      <p><strong>${compare.district}</strong> vs રાજ્ય સરેરાશ</p>
      <p>રોજગાર દિવસો: ${compare.days}</p>
      <p>મજૂરી: ₹${compare.wage}</p>
    `;
  }

  // ---------------- Help Overlay ----------------
  const helpOverlay = document.getElementById('help-overlay');
  document.getElementById('footer-help').onclick = () => helpOverlay.classList.add('active');
  document.getElementById('close-help').onclick = () => helpOverlay.classList.remove('active');

  // ---------------- Language Selector ----------------
  const langLinks = document.querySelectorAll('.lang-selector a');
  // restore saved language if present
  const savedLang = localStorage.getItem('lang');
  if (savedLang) {
    document.documentElement.lang = savedLang;
    langLinks.forEach(a => a.classList.toggle('active', a.getAttribute('lang') === savedLang));
  }
  langLinks.forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const lang = a.getAttribute('lang');
      document.documentElement.lang = lang;
      langLinks.forEach(x => x.classList.remove('active'));
      a.classList.add('active');
      localStorage.setItem('lang', lang);
    });
  });
});
