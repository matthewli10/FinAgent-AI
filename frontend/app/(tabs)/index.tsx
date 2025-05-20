import React from 'react';
import { SafeAreaView } from 'react-native';
import TranscriptForm from '../../components/TranscriptForm';

export default function HomeTab() {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TranscriptForm />
    </SafeAreaView>
  );
}
