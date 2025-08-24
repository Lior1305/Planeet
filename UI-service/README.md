# Planeet UI - React Application

A modern React application for planning amazing outings together. This is a complete refactor of the original vanilla HTML/JavaScript application.

## Features

- **Multi-step Planning Form**: Create outing plans with a 6-step wizard
- **User Authentication**: User context management with localStorage
- **Responsive Design**: Modern UI with CSS custom properties
- **React Router**: Client-side routing between pages
- **Component-based Architecture**: Reusable React components

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Header.jsx      # Navigation header
│   ├── PlanningModal.jsx # Multi-step planning form
│   └── SettingsModal.jsx # User settings modal
├── contexts/           # React contexts
│   └── UserContext.jsx # User authentication context
├── pages/              # Page components
│   ├── HomePage.jsx    # Landing page
│   ├── PlanPage.jsx    # Planning page
│   ├── DashboardHub.jsx # User dashboard
│   ├── ProfilePage.jsx # User profile
│   └── HistoryPage.jsx # Outing history
├── App.jsx             # Main app component with routing
└── main.jsx            # React entry point
```

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Key Components

### PlanningModal
The multi-step planning form with:
- Step-by-step navigation
- Form validation
- City geocoding
- Venue type selection
- Preferences and special requirements

### UserContext
Manages user authentication state:
- User login/logout
- Profile updates
- Persistent storage with localStorage

### Routing
Client-side routing between:
- `/` - Home page
- `/plan` - Planning page
- `/dashboard` - User dashboard
- `/profile` - User profile
- `/history` - Outing history

## Styling

The application uses the existing `styles.css` file with:
- CSS custom properties for theming
- Responsive design
- Modern animations and transitions
- Consistent component styling

## Development Notes

- **State Management**: Uses React hooks (useState, useEffect) and context
- **Form Handling**: Controlled components with validation
- **Navigation**: React Router for client-side routing
- **Authentication**: Simple localStorage-based auth (can be enhanced with real backend)

## Future Enhancements

- Real backend integration
- User authentication with JWT
- Database persistence
- Real-time features
- Enhanced form validation
- Error boundaries
- Unit testing

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `vite.config.js`
2. **Build errors**: Ensure all dependencies are installed
3. **Styling issues**: Check that `styles.css` is properly linked

### Getting Help

If you encounter issues:
1. Check the browser console for errors
2. Verify all dependencies are installed
3. Ensure Node.js version is compatible
4. Check file paths and imports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
