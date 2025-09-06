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
      console.log('via url:', `${configService.getUsersServiceUrl()}/users`);
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
        let errorMessage = 'Registration failed. Please try again.';
        
        // First, try to get the response text
        const responseText = await response.text();
        console.error('User creation failed:', responseText);
        
        try {
          // Try to parse as JSON
          const errorData = JSON.parse(responseText);
          
          // Handle specific backend error messages
          if (errorData.message) {
            if (errorData.message.includes('email') && errorData.message.includes('already')) {
              errorMessage = 'This email address is already registered. Please use a different email or try logging in.';
            } else if (errorData.message.includes('username') && errorData.message.includes('already')) {
              errorMessage = 'This username is already taken. Please choose a different username.';
            } else if (errorData.message.includes('email') && errorData.message.includes('invalid')) {
              errorMessage = 'Please enter a valid email address.';
            } else if (errorData.message.includes('username') && errorData.message.includes('invalid')) {
              errorMessage = 'Username must be at least 3 characters long and contain only letters, numbers, and underscores.';
            } else if (errorData.message.includes('password')) {
              errorMessage = 'Password must be at least 6 characters long.';
            } else {
              errorMessage = errorData.message;
            }
          }
        } catch (parseError) {
          // If we can't parse as JSON, use status codes and response text
          console.error('Could not parse error response as JSON:', parseError);
          
          if (response.status === 409) {
            errorMessage = 'This email is already in use. Please choose a different email.';
          } else if (response.status === 400) {
            errorMessage = 'Please check your information and try again.';
          } else if (response.status === 422) {
            errorMessage = 'Invalid information provided. Please check your details.';
          } else if (responseText) {
            // Use the raw response text if available
            errorMessage = responseText;
          }
        }
        
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Registration error:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return { success: false, error: 'Unable to connect to the server. Please check your internet connection and try again.' };
      }
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
        
        // Check if username exists first
        const userExists = users.find(u => u.username === username);
        if (!userExists) {
          console.log('Login failed: Username not found');
          return { success: false, error: 'Username not found. Please check your username or create a new account.' };
        }
        
        // Check if password matches
        const user = users.find(u => u.username === username && u.password === password);
        if (user) {
          console.log('Login successful:', user);
          this.saveUserToStorage(user);
          return { success: true, user };
        } else {
          console.log('Login failed: Incorrect password');
          return { success: false, error: 'Incorrect password. Please try again or reset your password.' };
        }
      } else {
        console.error('Login failed: API error');
        return { success: false, error: 'Unable to connect to the server. Please try again later.' };
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return { success: false, error: 'Unable to connect to the server. Please check your internet connection and try again.' };
      }
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
    
    // Check for required fields
    if (!username || !password || !email) {
      const missingFields = [];
      if (!username) missingFields.push('username');
      if (!password) missingFields.push('password');
      if (!email) missingFields.push('email');
      return { isValid: false, error: `Please fill in: ${missingFields.join(', ')}.` };
    }

    // Username validation
    if (username.length < 3) {
      return { isValid: false, error: "Username must be at least 3 characters long." };
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return { isValid: false, error: "Username can only contain letters, numbers, and underscores." };
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return { isValid: false, error: "Please enter a valid email address (e.g., user@example.com)." };
    }

    // Password validation
    if (password.length < 6) {
      return { isValid: false, error: "Password must be at least 6 characters long." };
    }
    if (password.length > 50) {
      return { isValid: false, error: "Password must be less than 50 characters." };
    }

    // Phone validation (optional)
    if (phone && !/^05\d{8}$/.test(phone)) {
      return { isValid: false, error: "Please enter a valid Israeli phone number (e.g., 05XXXXXXXX) or leave it empty." };
    }

    return { isValid: true };
  }

  validateLoginData(username, password) {
    if (!username && !password) {
      return { isValid: false, error: "Please enter both username and password." };
    }
    if (!username) {
      return { isValid: false, error: "Please enter your username." };
    }
    if (!password) {
      return { isValid: false, error: "Please enter your password." };
    }
    return { isValid: true };
  }
}

// Create and export user service instance
const userService = new UserService();

export default userService;
