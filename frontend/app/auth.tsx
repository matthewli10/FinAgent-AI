import { Redirect } from 'expo-router';
import Auth from '../components/Auth';
import { useAuth } from '../hooks/useAuth';

export default function AuthScreen() {
  const { user } = useAuth();

  // If user is already authenticated, redirect to home
  if (user) {
    return <Redirect href="/" />;
  }

  return <Auth />;
} 