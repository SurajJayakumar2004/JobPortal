/**
 * Main application component that sets up routing and global state.
 * Defines all application routes and wraps components with necessary providers.
 */

import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import NetworkStatus from './components/NetworkStatus';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegistrationPage from './pages/RegistrationPage';
import DashboardPage from './pages/DashboardPage';
import EmployerDashboard from './pages/EmployerDashboard';
import JobDetailsPage from './pages/JobDetailsPage';

function App() {
  return (
    <ErrorBoundary 
      componentName="App"
      showErrorDetails={false}
      onGoBack={() => window.location.href = '/'}
    >
      <ToastProvider>
        <AuthProvider>
          <div className="App">
            <NetworkStatus />
            <Navbar />
            <main className="main-content">
              <Routes>
                {/* Public routes */}
                <Route 
                  path="/" 
                  element={
                    <ErrorBoundary componentName="HomePage">
                      <HomePage />
                    </ErrorBoundary>
                  } 
                />
                <Route 
                  path="/login" 
                  element={
                    <ErrorBoundary componentName="LoginPage">
                      <LoginPage />
                    </ErrorBoundary>
                  } 
                />
                <Route 
                  path="/register" 
                  element={
                    <ErrorBoundary componentName="RegistrationPage">
                      <RegistrationPage />
                    </ErrorBoundary>
                  } 
                />
                <Route 
                  path="/jobs/:id" 
                  element={
                    <ErrorBoundary componentName="JobDetailsPage">
                      <JobDetailsPage />
                    </ErrorBoundary>
                  } 
                />
                
                {/* Protected routes - require authentication */}
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute>
                      <ErrorBoundary componentName="DashboardPage">
                        <DashboardPage />
                      </ErrorBoundary>
                    </ProtectedRoute>
                  } 
                />

                {/* Employer-specific dashboard */}
                <Route 
                  path="/employer" 
                  element={
                    <ProtectedRoute>
                      <ErrorBoundary componentName="EmployerDashboard">
                        <EmployerDashboard />
                      </ErrorBoundary>
                    </ProtectedRoute>
                  } 
                />
                
                {/* Catch-all route for 404 pages */}
                <Route path="*" element={
                  <ErrorBoundary componentName="NotFound">
                    <div className="container mx-auto px-4 py-8 text-center">
                      <h1 className="text-4xl font-bold text-gray-900 mb-4">404 - Page Not Found</h1>
                      <p className="text-gray-600 mb-6">The page you're looking for doesn't exist.</p>
                      <button 
                        onClick={() => window.location.href = '/'}
                        className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700"
                      >
                        Go Home
                      </button>
                    </div>
                  </ErrorBoundary>
                } />
              </Routes>
            </main>
          </div>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
