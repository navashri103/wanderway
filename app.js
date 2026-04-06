const API = 'https://wanderway-backend.up.railway.app';

function getToken() { return localStorage.getItem('token'); }
function getUser()  { return JSON.parse(localStorage.getItem('user') || 'null'); }

function saveAuth(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = 'login.html';
}

async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  const token = getToken();
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body)  opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Something went wrong');
  return data;
}

function showAlert(msg, type = 'success', containerId = 'alert-box') {
  const box = document.getElementById(containerId);
  if (!box) return;
  box.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
  setTimeout(() => box.innerHTML = '', 4000);
}

function updateNav() {
  const u = getUser();
  const el = document.getElementById('nav-user');
  if (!el) return;
  if (u) el.textContent = 'Hi, ' + u.name.split(' ')[0];
}

function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

// ── LOGIN / REGISTER ──
async function handleLogin(e) {
  e.preventDefault();
  try {
    const data = await api('/auth/login', 'POST', {
      email:    document.getElementById('login-email').value,
      password: document.getElementById('login-password').value
    });
    saveAuth(data.token, data.user);
    showAlert('Login successful! Redirecting...', 'success');
    setTimeout(() => window.location.href = 'index.html', 900);
  } catch (err) { showAlert(err.message, 'error'); }
}

async function handleRegister(e) {
  e.preventDefault();
  try {
    await api('/auth/register', 'POST', {
      name:     document.getElementById('reg-name').value,
      email:    document.getElementById('reg-email').value,
      phone:    document.getElementById('reg-phone').value,
      password: document.getElementById('reg-password').value
    });
    showAlert('Account created! Please login.', 'success');
    setTimeout(() => switchTab('login'), 1100);
  } catch (err) { showAlert(err.message, 'error'); }
}

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  document.getElementById(`panel-${tab}`).classList.remove('hidden');
}

// ── DESTINATIONS ──
async function loadDestinations(query = '') {
  const grid = document.getElementById('destinations-grid');
  if (!grid) return;
  grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">Loading...</p>';
  try {
    const data = await api(`/destinations?q=${query}`);
    if (!data.length) { grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">No destinations found.</p>'; return; }
    grid.innerHTML = data.map(d => `
      <div class="card dest-card" onclick="showDetail('${d._id}')">
        <img class="card-img" src="${d.image || ''}" alt="${d.name}" onerror="this.style.display='none'"/>
        <div class="card-body">
          <div class="card-tag">${d.category} &middot; ${d.state || ''}</div>
          <div class="card-title">${d.name}</div>
          <div class="card-desc">${(d.description||'').substring(0,90)}...</div>
          <div class="card-footer">
            <div class="card-price">&#8377;${d.price.toLocaleString()} <small>/person</small></div>
            <span style="font-size:0.78rem;color:var(--primary-light);font-weight:700;">View details →</span>
          </div>
        </div>
      </div>`).join('');
  } catch (err) {
    grid.innerHTML = `<p class="alert alert-error">${err.message}</p>`;
  }
}

// ── HOTELS ──
async function loadHotels(query = '') {
  const grid = document.getElementById('hotels-grid');
  if (!grid) return;
  grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">Loading...</p>';
  try {
    const data = await api(`/hotels?q=${query}`);
    if (!data.length) { grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">No hotels found.</p>'; return; }
    grid.innerHTML = data.map(h => `
      <div class="card">
        <img class="card-img" src="${h.image || ''}" alt="${h.name}" onerror="this.style.display='none'"/>
        <div class="card-body">
          <div class="card-tag">${'⭐'.repeat(h.stars)} &middot; ${h.location}</div>
          <div class="card-title">${h.name}</div>
          <div class="card-desc">${h.description}</div>
          <div class="card-footer">
            <div class="card-price">&#8377;${h.price_per_night.toLocaleString()} <small>/night</small></div>
            <button class="btn btn-primary btn-sm" onclick='openBookingModal(${JSON.stringify(h)}, "hotel")'>Book</button>
          </div>
        </div>
      </div>`).join('');
  } catch (err) {
    grid.innerHTML = `<p class="alert alert-error">${err.message}</p>`;
  }
}

// ── CABS ──
async function loadCabs(query = '') {
  const grid = document.getElementById('cabs-grid');
  if (!grid) return;
  grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">Loading...</p>';
  try {
    const data = await api(`/cabs?q=${query}`);
    if (!data.length) { grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">No cabs found.</p>'; return; }
    grid.innerHTML = data.map(c => `
      <div class="card">
        <img class="card-img" src="${c.image || ''}" alt="${c.name}" onerror="this.style.display='none'"/>
        <div class="card-body">
          <div class="card-tag">${c.type} &middot; ${c.seats} seats</div>
          <div class="card-title">${c.name}</div>
          <div class="card-desc">${c.description}</div>
          <div class="card-footer">
            <div class="card-price">&#8377;${c.price_per_km} <small>/km</small></div>
            <button class="btn btn-primary btn-sm" onclick='openBookingModal(${JSON.stringify(c)}, "cab")'>Book</button>
          </div>
        </div>
      </div>`).join('');
  } catch (err) {
    grid.innerHTML = `<p class="alert alert-error">${err.message}</p>`;
  }
}

// ── COMBOS ──
async function loadCombos() {
  const grid = document.getElementById('combos-grid');
  if (!grid) return;
  grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">Loading...</p>';
  try {
    const data = await api('/combos');
    if (!data.length) { grid.innerHTML = '<p class="text-muted text-center" style="padding:2rem">No combos available.</p>'; return; }
    grid.innerHTML = data.map(c => `
      <div class="combo-card">
        <img class="combo-img" src="${c.image || ''}" alt="${c.name}" onerror="this.style.display='none'"/>
        <div class="combo-header">
          <h3>${c.name}</h3>
          <p style="color:rgba(255,255,255,0.65);font-size:0.85rem;margin-bottom:0.5rem">${c.destination} &middot; ${c.duration} days</p>
          <div class="combo-price">&#8377;${c.total_price.toLocaleString()} <small>/person</small></div>
        </div>
        <div class="combo-includes"><ul>${c.includes.map(i => `<li>${i}</li>`).join('')}</ul></div>
        <div class="combo-footer">
          <button class="btn btn-primary btn-full" onclick='openBookingModal(${JSON.stringify(c)}, "combo")'>Book Combo</button>
        </div>
      </div>`).join('');
  } catch (err) {
    grid.innerHTML = `<p class="alert alert-error">${err.message}</p>`;
  }
}

// ── BOOKING MODAL ──
let currentItem = null;
let currentType = null;

function openBookingModal(item, type) {
  if (!getToken()) { window.location.href = 'login.html'; return; }
  currentItem = item;
  currentType = type;
  document.getElementById('booking-item-name').textContent = item.name;
  document.getElementById('booking-type-label').textContent =
    type === 'hotel' ? 'Number of Nights' : type === 'cab' ? 'Distance (km)' : 'Number of Persons';
  const priceKey = type === 'hotel' ? 'price_per_night' : type === 'cab' ? 'price_per_km' : type === 'combo' ? 'total_price' : 'price';
  document.getElementById('booking-unit-price').textContent = '&#8377;' + (item[priceKey] || 0).toLocaleString();
  updateBookingTotal();
  openModal('booking-modal');
}

function updateBookingTotal() {
  if (!currentItem) return;
  const qty = parseInt(document.getElementById('booking-qty').value) || 1;
  const priceKey = currentType === 'hotel' ? 'price_per_night' : currentType === 'cab' ? 'price_per_km' : currentType === 'combo' ? 'total_price' : 'price';
  const total = (currentItem[priceKey] || 0) * qty;
  document.getElementById('booking-total').textContent = '&#8377;' + total.toLocaleString();
}

async function submitBooking(e) {
  e.preventDefault();
  const date  = document.getElementById('booking-date').value;
  const qty   = parseInt(document.getElementById('booking-qty').value) || 1;
  const notes = document.getElementById('booking-notes').value;
  const priceKey = currentType === 'hotel' ? 'price_per_night' : currentType === 'cab' ? 'price_per_km' : currentType === 'combo' ? 'total_price' : 'price';
  const total = (currentItem[priceKey] || 0) * qty;
  try {
    await api('/bookings', 'POST', { type: currentType, item_id: currentItem._id, item_name: currentItem.name, date, qty, notes, total_price: total });
    closeModal('booking-modal');
    showAlert('Booking confirmed! 🎉', 'success', 'page-alert');
  } catch (err) {
    showAlert(err.message, 'error', 'modal-alert');
  }
}

// ── MY BOOKINGS ──
async function loadMyBookings() {
  const tbody = document.getElementById('bookings-tbody');
  if (!tbody) return;
  try {
    const data = await api('/bookings/mine');
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted" style="padding:2rem">No bookings yet. Go book something!</td></tr>';
      return;
    }
    tbody.innerHTML = data.map(b => `
      <tr>
        <td><strong>${b.item_name}</strong></td>
        <td><span class="badge badge-warning">${b.type}</span></td>
        <td>${b.date}</td>
        <td>${b.qty}</td>
        <td><strong>&#8377;${b.total_price.toLocaleString()}</strong></td>
        <td>
          <span class="badge ${b.status === 'confirmed' ? 'badge-success' : 'badge-danger'}">${b.status}</span>
          ${b.status !== 'cancelled' ? `<button class="btn btn-danger btn-sm mt-1" onclick="cancelBooking('${b._id}')">Cancel</button>` : ''}
        </td>
      </tr>`).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6"><p class="alert alert-error">${err.message}</p></td></tr>`;
  }
}

async function cancelBooking(id) {
  if (!confirm('Are you sure you want to cancel this booking?')) return;
  try {
    await api(`/bookings/${id}/cancel`, 'PUT');
    showAlert('Booking cancelled.', 'success', 'page-alert');
    loadMyBookings();
  } catch (err) {
    showAlert(err.message, 'error', 'page-alert');
  }
}

// ── ADMIN ──
async function loadAdminStats() {
  try {
    const data = await api('/admin/stats');
    document.getElementById('stat-users').textContent        = data.users;
    document.getElementById('stat-bookings').textContent     = data.bookings;
    document.getElementById('stat-revenue').textContent      = '&#8377;' + data.revenue.toLocaleString();
    document.getElementById('stat-destinations').textContent = data.destinations;
  } catch {}
}

async function loadAdminBookings() {
  const tbody = document.getElementById('admin-bookings-tbody');
  if (!tbody) return;
  try {
    const data = await api('/admin/bookings');
    if (!data.length) { tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted" style="padding:1rem">No bookings yet.</td></tr>'; return; }
    tbody.innerHTML = data.map(b => `
      <tr>
        <td>${b.user_name}</td><td>${b.item_name}</td><td>${b.type}</td>
        <td>${b.date}</td><td>&#8377;${b.total_price.toLocaleString()}</td>
        <td><span class="badge ${b.status === 'confirmed' ? 'badge-success' : 'badge-danger'}">${b.status}</span></td>
      </tr>`).join('');
  } catch {}
}

async function loadAdminUsers() {
  const tbody = document.getElementById('admin-users-tbody');
  if (!tbody) return;
  try {
    const data = await api('/admin/users');
    tbody.innerHTML = data.map(u => `
      <tr>
        <td>${u.name}</td><td>${u.email}</td><td>${u.phone || '-'}</td>
        <td><span class="badge ${u.role === 'admin' ? 'badge-danger' : 'badge-success'}">${u.role}</span></td>
      </tr>`).join('');
  } catch {}
}

async function addDestination(e) {
  e.preventDefault();
  const body = { name: document.getElementById('d-name').value, category: document.getElementById('d-category').value, description: document.getElementById('d-description').value, price: parseFloat(document.getElementById('d-price').value), emoji: document.getElementById('d-emoji').value || '🌍' };
  try { await api('/admin/destinations', 'POST', body); showAlert('Destination added!', 'success', 'admin-alert'); e.target.reset(); }
  catch (err) { showAlert(err.message, 'error', 'admin-alert'); }
}

async function addHotel(e) {
  e.preventDefault();
  const body = { name: document.getElementById('h-name').value, location: document.getElementById('h-location').value, stars: parseInt(document.getElementById('h-stars').value), description: document.getElementById('h-description').value, price_per_night: parseFloat(document.getElementById('h-price').value) };
  try { await api('/admin/hotels', 'POST', body); showAlert('Hotel added!', 'success', 'admin-alert'); e.target.reset(); }
  catch (err) { showAlert(err.message, 'error', 'admin-alert'); }
}

async function addCab(e) {
  e.preventDefault();
  const body = { name: document.getElementById('c-name').value, type: document.getElementById('c-type').value, seats: parseInt(document.getElementById('c-seats').value), description: document.getElementById('c-description').value, price_per_km: parseFloat(document.getElementById('c-price').value) };
  try { await api('/admin/cabs', 'POST', body); showAlert('Cab added!', 'success', 'admin-alert'); e.target.reset(); }
  catch (err) { showAlert(err.message, 'error', 'admin-alert'); }
}

async function addCombo(e) {
  e.preventDefault();
  const includes = document.getElementById('co-includes').value.split('\n').filter(Boolean);
  const body = { name: document.getElementById('co-name').value, destination: document.getElementById('co-destination').value, duration: parseInt(document.getElementById('co-duration').value), total_price: parseFloat(document.getElementById('co-price').value), includes };
  try { await api('/admin/combos', 'POST', body); showAlert('Combo added!', 'success', 'admin-alert'); e.target.reset(); }
  catch (err) { showAlert(err.message, 'error', 'admin-alert'); }
}

function adminShowSection(section) {
  document.querySelectorAll('.admin-section').forEach(s => s.classList.add('hidden'));
  document.getElementById('section-' + section).classList.remove('hidden');
  document.querySelectorAll('.admin-sidebar a').forEach(a => a.classList.remove('active'));
  const el = document.querySelector(`[data-section="${section}"]`);
  if (el) el.classList.add('active');
}

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  updateNav();
  const lf = document.getElementById('login-form');
  if (lf) lf.addEventListener('submit', handleLogin);
  const rf = document.getElementById('register-form');
  if (rf) rf.addEventListener('submit', handleRegister);
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => switchTab(t.dataset.tab)));

  loadDestinations();
  const ds = document.getElementById('dest-search');
  if (ds) ds.addEventListener('input', e => loadDestinations(e.target.value));

  loadHotels();
  const hs = document.getElementById('hotel-search');
  if (hs) hs.addEventListener('input', e => loadHotels(e.target.value));

  loadCabs();
  const cs = document.getElementById('cab-search');
  if (cs) cs.addEventListener('input', e => loadCabs(e.target.value));

  loadCombos();
  loadMyBookings();

  const qi = document.getElementById('booking-qty');
  if (qi) qi.addEventListener('input', updateBookingTotal);
  const bf = document.getElementById('booking-form');
  if (bf) bf.addEventListener('submit', submitBooking);

  loadAdminStats();
  loadAdminBookings();
  loadAdminUsers();
  const dForm = document.getElementById('add-destination-form');
  if (dForm) dForm.addEventListener('submit', addDestination);
  const hForm = document.getElementById('add-hotel-form');
  if (hForm) hForm.addEventListener('submit', addHotel);
  const cForm = document.getElementById('add-cab-form');
  if (cForm) cForm.addEventListener('submit', addCab);
  const coForm = document.getElementById('add-combo-form');
  if (coForm) coForm.addEventListener('submit', addCombo);

  document.querySelectorAll('.logout-btn').forEach(b => b.addEventListener('click', logout));
});
