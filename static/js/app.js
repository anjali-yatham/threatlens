// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
  // Hide ALL pages first
  hideAllPages();
  
  // Check if already logged in
  if (localStorage.getItem('isLoggedIn') === 'true') {
    showPage('page-app');
  } else {
    showPage('page-auth');
  }
  
  // Generate particles
  generateParticles();
});

function hideAllPages() {
  var pages = document.querySelectorAll('.page');
  pages.forEach(function(page) {
    page.style.display = 'none';
    page.classList.remove('active');
  });
}

function showPage(pageId) {
  // Hide all pages first
  hideAllPages();
  
  // Show the requested page
  var page = document.getElementById(pageId);
  if (page) {
    page.style.display = 'block';
    page.classList.add('active');
  }
  
  // Scroll to top
  window.scrollTo(0, 0);
}

function login() {
  var email = document.getElementById('login-email').value.trim();
  var pass = document.getElementById('login-pass').value.trim();
  var err = document.getElementById('login-error');
  
  if (email === 'admin@threatlens.com' && pass === 'password123') {
    localStorage.setItem('isLoggedIn', 'true');
    if (err) {
      err.style.display = 'none';
    }
    showPage('page-app');
  } else {
    if (err) {
      err.style.display = 'block';
      err.textContent = 'Wrong credentials! Try admin@threatlens.com / password123';
    }
  }
}

function signup() {
  var name = document.getElementById('signup-name').value.trim();
  if (!name) {
    alert('Please enter your name');
    return;
  }
  localStorage.setItem('isLoggedIn', 'true');
  showPage('page-app');
}

function logout() {
  localStorage.clear();
  showPage('page-auth');
}

function switchTab(type) {
  // Remove active from all tabs and content
  document.querySelectorAll('.tab').forEach(function(t) {
    t.classList.remove('active');
  });
  document.querySelectorAll('.tab-content').forEach(function(c) {
    c.classList.remove('active');
    c.style.display = 'none';
  });
  
  // Activate clicked tab
  var clickedTab = event.target.closest('.tab');
  if (clickedTab) {
    clickedTab.classList.add('active');
  }
  
  // Show tab content
  var content = document.getElementById('tab-' + type);
  if (content) {
    content.classList.add('active');
    content.style.display = 'block';
  }
  
  // Hide result box
  var rb = document.getElementById('result-box');
  if (rb) {
    rb.style.display = 'none';
    rb.innerHTML = '';
  }
}

function analyze(type) {
  var inputIds = {
    url: 'url-input',
    email: 'email-input', 
    scam: 'scam-input',
    job: 'job-input'
  };
  var endpoints = {
    url: '/predict-url',
    email: '/predict-email',
    scam: '/predict-scam',
    job: '/predict-job'
  };
  
  var inputEl = document.getElementById(inputIds[type]);
  if (!inputEl) return;
  
  var value = inputEl.value.trim();
  if (!value) {
    inputEl.style.borderColor = '#ff4444';
    setTimeout(function() {
      inputEl.style.borderColor = 'rgba(0,212,255,0.3)';
    }, 2000);
    return;
  }
  
  var rb = document.getElementById('result-box');
  rb.style.display = 'block';
  rb.innerHTML = '<div style="padding:32px;text-align:center;color:#00d4ff;">' +
    '<div style="display:inline-block;width:32px;height:32px;border:3px solid rgba(0,212,255,0.2);' +
    'border-top-color:#00d4ff;border-radius:50%;animation:spin 1s linear infinite;margin-bottom:12px;"></div>' +
    '<div>Analyzing with AI...</div></div>';
  
  var body = type === 'url' ? {url: value} : {text: value};
  
  fetch(endpoints[type], {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    var threats = ['Phishing', 'Spam/Phishing', 'Fake'];
    var isThreat = threats.includes(data.result);
    
    if (isThreat) {
      rb.innerHTML = 
        '<div style="background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.4);' +
        'padding:32px;text-align:center;border-radius:16px;box-shadow:0 0 30px rgba(255,68,68,0.1);">' +
        '<div style="font-size:3rem;margin-bottom:12px;">⚠️</div>' +
        '<div style="font-family:Orbitron,monospace;font-size:1.8rem;font-weight:700;color:#ff4444;margin-bottom:8px;">THREAT DETECTED</div>' +
        '<div style="color:#ff6666;font-size:1.1rem;margin-bottom:8px;">' + data.result + '</div>' +
        '<div style="color:rgba(224,230,240,0.6);">Confidence: ' + data.confidence + '%</div>' +
        '</div>';
    } else {
      rb.innerHTML = 
        '<div style="background:rgba(0,255,136,0.08);border:1px solid rgba(0,255,136,0.4);' +
        'padding:32px;text-align:center;border-radius:16px;box-shadow:0 0 30px rgba(0,255,136,0.08);">' +
        '<div style="font-size:3rem;margin-bottom:12px;">✅</div>' +
        '<div style="font-family:Orbitron,monospace;font-size:1.8rem;font-weight:700;color:#00ff88;margin-bottom:8px;">SAFE</div>' +
        '<div style="color:#00cc6a;font-size:1.1rem;margin-bottom:8px;">' + data.result + '</div>' +
        '<div style="color:rgba(224,230,240,0.6);">Confidence: ' + data.confidence + '%</div>' +
        '</div>';
    }
  })
  .catch(function() {
    rb.innerHTML = 
      '<div style="background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.4);' +
      'padding:20px;text-align:center;border-radius:16px;">' +
      '<div style="color:#ff4444;">Error occurred. Please try again.</div></div>';
  });
}

function generateParticles() {
  var bg = document.getElementById('cyber-bg');
  if (!bg) return;
  
  for (var i = 0; i < 40; i++) {
    var p = document.createElement('div');
    p.className = 'particle';
    var size = Math.random() * 3 + 1;
    var color = Math.random() > 0.5 ? '#00d4ff' : '#7b2fff';
    p.style.cssText = 
      'left:' + (Math.random() * 100) + '%;' +
      'width:' + size + 'px;' +
      'height:' + size + 'px;' +
      'background:' + color + ';' +
      'box-shadow:0 0 ' + (size*2) + 'px ' + color + ';' +
      'animation-duration:' + (Math.random() * 15 + 8) + 's;' +
      'animation-delay:-' + (Math.random() * 15) + 's;';
    bg.appendChild(p);
  }
}

// Enter key support
document.addEventListener('keydown', function(e) {
  if (e.key !== 'Enter') return;
  var loginPage = document.getElementById('page-login');
  var signupPage = document.getElementById('page-signup');
  if (loginPage && loginPage.classList.contains('active')) login();
  if (signupPage && signupPage.classList.contains('active')) signup();
});

// Add spin keyframe
var style = document.createElement('style');
style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
document.head.appendChild(style);