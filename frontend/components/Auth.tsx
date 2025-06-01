import React, { useState } from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from 'firebase/auth';
import { auth } from '../services/firebase';
import { ThemedText } from './ThemedText';
import { ThemedView } from './ThemedView';
import { useAuth } from '../hooks/useAuth';

export default function Auth() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [successMsg, setSuccessMsg] = useState('');
  const { user } = useAuth();

  const handleAuth = async () => {
    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
        // On success, user will be redirected by auth context
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
        setSuccessMsg('Account created! Please log in.');
        setIsLogin(true);
        setEmail('');
        setPassword('');
      }
    } catch (error: any) {
      if (isLogin) {
        Alert.alert('Login Failed', error.message);
      } else {
        Alert.alert('Signup Failed', error.message);
      }
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error: any) {
      Alert.alert('Error', error.message);
    }
  };

  if (user) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText style={styles.title}>Welcome!</ThemedText>
        <ThemedText style={styles.subtitle}>You are logged in as {user.email}</ThemedText>
        <TouchableOpacity style={[styles.button, styles.logoutButton]} onPress={handleLogout}>
          <ThemedText style={styles.buttonText}>Logout</ThemedText>
        </TouchableOpacity>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <ThemedText style={styles.title}>
        {isLogin ? 'Welcome Back!' : 'Create Account'}
      </ThemedText>
      {successMsg ? (
        <ThemedText style={styles.successMsg}>{successMsg}</ThemedText>
      ) : null}
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <TouchableOpacity style={styles.button} onPress={handleAuth}>
        <ThemedText style={styles.buttonText}>
          {isLogin ? 'Login' : 'Sign Up'}
        </ThemedText>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => { setIsLogin(!isLogin); setSuccessMsg(''); }}>
        <ThemedText style={styles.switchText}>
          {isLogin ? 'Need an account? Sign Up' : 'Have an account? Login'}
        </ThemedText>
      </TouchableOpacity>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
    opacity: 0.7,
  },
  successMsg: {
    color: 'green',
    textAlign: 'center',
    marginBottom: 10,
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  logoutButton: {
    backgroundColor: '#FF3B30',
  },
  buttonText: {
    color: '#fff',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  switchText: {
    marginTop: 20,
    textAlign: 'center',
    color: '#007AFF',
  },
}); 