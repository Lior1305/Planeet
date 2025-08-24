# Planeet UI Service - React Version

This is the React-based version of the Planeet UI service, converted from the original vanilla HTML/JavaScript implementation.

## Features

- **React 18** with modern hooks and functional components
- **React Router v6** for client-side routing
- **Responsive design** with CSS variables and modern styling
- **Service integration** with the existing backend services
- **User authentication** with localStorage persistence
- **Multi-step planning form** with validation
- **Kubernetes-ready** configuration detection

## Service Connections

The React app maintains the same service connections as the original:

- **Users Service**: Handles user registration, login, and authentication
- **Planning Service**: Creates outing plans via the planning API
- **Venues Service**: Available for future venue discovery features
- **Outing Profile Service**: Available for future profile features

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.js       # Navigation header
│   ├── Home.js         # Landing page
│   ├── Login.js        # User login form
│   ├── Register.js     # User registration form
│   ├── Plan.js         # Planning page
│   ├── History.js      # User's planning history
│   └── PlanningModal.js # Multi-step planning form
├── services/           # Service layer
│   ├── config.js       # Configuration and service URLs
│   ├── userService.js  # User authentication service
│   └── planningService.js # Planning service integration
├── App.js              # Main app component with routing
├── index.js            # App entry point
└── index.css           # Global styles
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- All backend services running (users, planning, venues, outing-profile)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
```

The build output will be in the `build/` directory.

## Configuration

The app automatically detects the environment and configures service URLs:

- **Local Development**: Uses localhost ports (8080, 8001, 8000, 5000)
- **Local Kubernetes**: Uses NodePort URLs (30001, 30002, 30003, 30004)
- **Production Kubernetes**: Uses Ingress paths (/api/users, /api/planning, etc.)

## Key Components

### PlanningModal
The multi-step planning form includes:
- Basic information (plan name, group size)
- Location (city, address with geocoding)
- Date and time selection
- Venue type selection
- Preferences (budget, rating, radius)
- Final review and submission

### User Authentication
- Login/Register forms with validation
- localStorage persistence
- Automatic redirects based on authentication status
- Protected routes for authenticated users

### Service Integration
- Maintains the same API contracts as the original
- Error handling and user feedback
- Loading states and form validation

## Migration Notes

### From Vanilla JS to React
- **State Management**: Replaced global variables with React state and hooks
- **Event Handling**: Converted inline onclick handlers to React event handlers
- **DOM Manipulation**: Replaced direct DOM manipulation with React state updates
- **Routing**: Implemented client-side routing with React Router
- **Component Architecture**: Broke down the monolithic structure into reusable components

### Preserved Functionality
- All service API calls remain the same
- Configuration detection logic is preserved
- Form validation rules are maintained
- User authentication flow is identical
- Planning form steps and logic are preserved

## Development

### Adding New Features
1. Create new components in `src/components/`
2. Add new services in `src/services/` if needed
3. Update routing in `App.js`
4. Add any new styles to `index.css`

### Styling
The app uses CSS variables for consistent theming. Key variables:
- `--primary`: Main brand color
- `--accent-*`: Accent colors
- `--text-*`: Text colors
- `--border`: Border colors
- `--background`: Background colors

### State Management
For simple state, use React's built-in `useState` and `useEffect`. For more complex state management, consider adding Redux or Zustand.

## Troubleshooting

### Common Issues

1. **Service Connection Errors**: Check that all backend services are running
2. **Build Errors**: Ensure Node.js version is 16+ and all dependencies are installed
3. **Routing Issues**: Verify that the app is served from the root path

### Debug Mode
Open browser DevTools to see detailed logging of service calls and configuration detection.

## Deployment

### Kubernetes
The app is ready for Kubernetes deployment with the existing configuration detection.

### Static Hosting
Build the app and serve the `build/` directory from any static hosting service.

## Future Enhancements

- Add Redux for state management
- Implement real-time updates
- Add offline support with service workers
- Enhance accessibility features
- Add unit and integration tests
