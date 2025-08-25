import configService from './config.js';

class UserService {
  constructor() {
    this.currentUser = null;
    this.loadUserFromStorage();
  }

  loadUserFromStorage() {
    try {
      const userData = localStorage.getItem('planeetUser');
      if (userData) {
        this.currentUser = JSON.parse(userData);
        console.log('User loaded from storage:', this.currentUser);
      }
    } catch (error) {
      console.error('Failed to load user from storage:', error);
      localStorage.removeItem('planeetUser');
    }
  }

  saveUserToStorage(user) {
    try {
      localStorage.setItem('planeetUser', JSON.stringify(user));
      this.currentUser = user;
      console.log('User saved to storage:', user);
    } catch (error) {
      console.error('Failed to save user to storage:', error);
    }
  }

  clearUser() {
    this.currentUser = null;
    localStorage.removeItem('planeetUser');
    console.log('User cleared from storage');
  }

  getCurrentUser() {
    return this.currentUser;
  }

  isAuthenticated() {
    return !!this.currentUser;
  }

  async register(userData) {
    try {
      console.log('Attempting to register user:', userData.username);
      
      const response = await fetch(`${configService.getUsersServiceUrl()}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        const user = await response.json();
        console.log('Registration successful:', user);
        this.saveUserToStorage(user);
        return { success: true, user };
      } else {
        const errorText = await response.text();
        console.error('User creation failed:', errorText);
        return { success: false, error: 'Registration failed. Please try again.' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Connection error. Please check if all services are running.' };
    }
  }

  async login(username, password) {
    try {
      console.log('Attempting to login user:', username);
      
      // Get all users and find the matching one
      const response = await fetch(`${configService.getUsersServiceUrl()}/users`);
      if (response.ok) {
        const users = await response.json();
        console.log('Retrieved users:', users);
        
        const user = users.find(u => u.username === username && u.password === password);
        
        if (user) {
          console.log('Login successful:', user);
          this.saveUserToStorage(user);
          return { success: true, user };
        } else {
          console.log('Login failed: Invalid credentials');
          return { success: false, error: 'Invalid username or password.' };
        }
      } else {
        console.error('Login failed: API error');
        return { success: false, error: 'Login failed. Please try again.' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Connection error. Please check if all services are running.' };
    }
  }

  logout() {
    this.clearUser();
    console.log('User logged out');
  }

  async updateUser(userId, userData) {
    try {
      console.log('Attempting to update user:', userId, userData);
      
      // Get current user to preserve password
      const currentUser = this.getCurrentUser();
      if (!currentUser) {
        return { success: false, error: 'No current user found' };
      }
      
      // Merge update data with existing user data, preserving password
      const updateData = {
        ...currentUser,
        ...userData,
        password: currentUser.password // Always preserve the password
      };
      
      const response = await fetch(`${configService.getUsersServiceUrl()}/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedUser = await response.json();
        console.log('User update successful:', updatedUser);
        this.saveUserToStorage(updatedUser);
        return { success: true, user: updatedUser };
      } else {
        const errorText = await response.text();
        console.error('User update failed:', errorText);
        return { success: false, error: 'Update failed. Please try again.' };
      }
    } catch (error) {
      console.error('Update error:', error);
      return { success: false, error: 'Connection error. Please check if all services are running.' };
    }
  }

  validateRegistrationData(userData) {
    const { username, password, email, phone } = userData;
    
    // Validation
    if (!username || !password || !email) {
      return { isValid: false, error: "Please fill in username, password, and email." };
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return { isValid: false, error: "Please enter a valid email address." };
    }

    // Phone validation (optional)
    if (phone && !/^05\d{8}$/.test(phone)) {
      return { isValid: false, error: "Please enter a valid Israeli phone number (e.g., 05XXXXXXXX) or leave it empty." };
    }

    return { isValid: true };
  }

  validateLoginData(username, password) {
    if (!username || !password) {
      return { isValid: false, error: "Please enter both username and password." };
    }
    return { isValid: true };
  }
}

// Create and export user service instance
const userService = new UserService();

export default userService;
