const getBackendUrl = () => {
  return window.location.origin;
};
 
export const API_BASE_URL = getBackendUrl();
export const FRONTEND_URL = window.location.origin; 