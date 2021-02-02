import settings from './settings';

export function login(token) {
  sessionStorage.setItem('token', token);
}

function deleteAllCookies() {
  const cookies = document.cookie.split(";");

  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i];
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
}

export function logout() {
  sessionStorage.clear();
  deleteAllCookies();
}

export function sessionRequest(url, options = {}) {
  options.headers = options.headers || {};
  if (options && options.data && typeof options.data == 'object') {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.data);
  }
  const token = sessionStorage.getItem('token');
  if (token) {
    options.headers.Authorization = "Token " + token;
  }
  return fetch(settings.serverRoot + url, options);
}

export default sessionRequest;
