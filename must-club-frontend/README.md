# MUST Science Innovators Club - Frontend Application

A modern React TypeScript frontend application for the Meru University Science Innovators Club, featuring both user and admin interfaces with a beautiful yellow/green/white theme.

## 🚀 Features

### User Features
- **Authentication System**: Secure login/registration with JWT tokens
- **User Dashboard**: Personalized dashboard with stats and quick actions
- **Events Management**: Browse, search, filter, and register for events
- **Communities**: Join and participate in tech communities
- **Blog**: Read articles and tech insights
- **Profile Management**: Update personal information and skills
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

### Admin Features
- **Admin Dashboard**: Comprehensive overview of club activities
- **User Management**: View and manage all registered users
- **Event Management**: Create, update, and manage events
- **Community Management**: Oversee all tech communities
- **Content Management**: Manage blog posts and articles
- **Feedback System**: Review and respond to user feedback
- **Partner Management**: Manage club partnerships
- **Testimonials**: Moderate user testimonials
- **Executive Management**: Manage club executives and positions

### Technical Features
- **Modern Stack**: React 18, TypeScript, Tailwind CSS
- **State Management**: Context API with custom hooks
- **API Integration**: Full REST API integration with error handling
- **Responsive UI**: Mobile-first design approach
- **Form Validation**: Comprehensive form validation with react-hook-form
- **Toast Notifications**: User-friendly notifications
- **Protected Routes**: Role-based access control
- **Loading States**: Smooth loading experiences
- **Error Boundaries**: Graceful error handling

## 🎨 Design Theme

The application uses a carefully crafted color scheme:
- **Primary (Yellow)**: `#f59e0b` - Used for main actions and highlights
- **Secondary (Green)**: `#22c55e` - Used for success states and secondary actions
- **Background**: White with subtle gradients using yellow and green tints
- **Text**: Black and various gray shades for optimal readability

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (version 16 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**
- **Git** - [Download here](https://git-scm.com/)
- A code editor like **Visual Studio Code** - [Download here](https://code.visualstudio.com/)

## 🛠️ Installation & Setup

### Step 1: Clone or Navigate to the Project
```bash
# If you're already in the project directory
cd /workspace/must-club-frontend

# Or if you need to clone from a repository
# git clone <repository-url>
# cd must-club-frontend
```

### Step 2: Install Dependencies
```bash
# Using npm
npm install

# Or using yarn
yarn install
```

### Step 3: Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
# The default API URL is set to http://localhost:8000
```

### Step 4: Start the Development Server
```bash
# Using npm
npm start

# Or using yarn
yarn start
```

The application will start on `http://localhost:3000` and automatically open in your browser.

## 🔧 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# App Configuration
REACT_APP_APP_NAME=MUST Science Innovators Club
REACT_APP_APP_VERSION=1.0.0

# Features
REACT_APP_ENABLE_SOCIAL_LOGIN=false
REACT_APP_ENABLE_NOTIFICATIONS=true

# Optional: OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
REACT_APP_GITHUB_CLIENT_ID=your_github_client_id
```

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Common components (Button, Card, etc.)
│   ├── auth/            # Authentication components
│   ├── user/            # User-specific components
│   └── admin/           # Admin-specific components
├── pages/               # Page components
│   ├── auth/            # Authentication pages
│   ├── user/            # User pages
│   └── admin/           # Admin pages
├── context/             # React Context providers
├── services/            # API services and HTTP client
├── hooks/               # Custom React hooks
├── utils/               # Utility functions and constants
├── types/               # TypeScript type definitions
└── styles/              # Global styles and Tailwind config
```

## 🎯 Getting Started (For React Beginners)

### What is React?
React is a JavaScript library for building user interfaces. It allows you to create interactive web applications using components.

### Key Concepts Used in This Project:

1. **Components**: Reusable pieces of UI (like buttons, forms, pages)
2. **Props**: Data passed from parent to child components
3. **State**: Data that can change over time
4. **Hooks**: Special functions that let you use React features
5. **Context**: A way to share data across many components
6. **TypeScript**: JavaScript with type checking for better code quality

### How to Make Changes:

1. **Styling**: We use Tailwind CSS for styling. You can modify classes in component files.
2. **Colors**: The main theme colors are defined in `tailwind.config.js`
3. **Components**: Modify existing components in the `src/components/` directory
4. **Pages**: Add or modify pages in the `src/pages/` directory
5. **API**: API calls are handled in `src/services/api.ts`

## 🔗 API Integration

The frontend connects to the Django backend API. Make sure your Django server is running on `http://localhost:8000` (or update the `REACT_APP_API_URL` in your `.env` file).

### API Endpoints Used:
- Authentication: `/api/account/`
- Events: `/api/events/`
- Communities: `/api/list-communities/`
- Blog: `/api/home/blog/`
- Admin endpoints: Various admin-specific endpoints

## 📱 Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject from Create React App (not recommended)
npm run eject

# Type checking
npx tsc --noEmit

# Lint code
npm run lint
```

## 🎨 Customizing the Theme

### Colors
Edit `tailwind.config.js` to change the color scheme:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#f59e0b', // Change this for different yellow
      },
      secondary: {
        500: '#22c55e', // Change this for different green
      }
    }
  }
}
```

### Fonts
The app uses Inter font. To change it, update the font import in `src/index.css` and the Tailwind config.

## 🔐 User Roles

### Regular Users Can:
- Register and login
- View and register for events
- Join communities
- Read blog posts
- Update their profile
- Submit feedback

### Admin Users Can:
- Access admin dashboard
- Manage all users
- Create and manage events
- Manage communities
- Write and manage blog posts
- Review feedback
- Manage partners and testimonials
- Manage club executives

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

This creates a `build` folder with optimized files ready for deployment.

### Deployment Options:
- **Netlify**: Drag and drop the build folder
- **Vercel**: Connect your GitHub repository
- **GitHub Pages**: Use the build folder
- **Traditional hosting**: Upload build folder contents

## 🐛 Troubleshooting

### Common Issues:

1. **Module not found errors**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port already in use**:
   ```bash
   # Kill process on port 3000
   npx kill-port 3000
   # Or use a different port
   PORT=3001 npm start
   ```

3. **API connection issues**:
   - Check if Django server is running on port 8000
   - Verify the `REACT_APP_API_URL` in your `.env` file
   - Check browser console for CORS errors

4. **Build errors**:
   ```bash
   # Clear cache and rebuild
   npm start -- --reset-cache
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add some feature'`
6. Push: `git push origin feature-name`
7. Submit a pull request

## 📚 Learning Resources

### React & TypeScript:
- [React Official Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

### Styling:
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com/)

### State Management:
- [React Context API](https://react.dev/reference/react/useContext)
- [Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)

## 📞 Support

If you encounter any issues or need help:

1. Check the troubleshooting section above
2. Look for similar issues in the project repository
3. Create a new issue with detailed information
4. Contact the development team

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Meru University Science Innovators Club
- React and TypeScript communities
- Tailwind CSS team
- All contributors and club members

---

**Happy Coding! 🚀**

*Built with ❤️ for the MUST Science Innovators Community*