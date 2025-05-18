// frontend/src/utils/tokenChecker.js
export const checkToken = () => {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user'));
  
  if (!token) {
    console.error("No token found");
    return false;
  }
  
  if (!user) {
    console.error("No user data found");
    return false;
  }
  
  console.log("Token exists:", !!token);
  console.log("User data:", user);
  console.log("Is admin flag:", user.is_admin);
  
  return true;
}
