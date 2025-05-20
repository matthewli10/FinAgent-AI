import React, { useState } from 'react';
import { View, TextInput, Button, Text, ScrollView, ActivityIndicator } from 'react-native';
import { summarizeTranscript } from '../services/api';

export default function TranscriptForm() {
  const [ticker, setTicker] = useState('');
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setSummary('');
    const result = await summarizeTranscript(ticker, transcript);
    setSummary(result?.summary || 'Error generating summary.');
    setLoading(false);
  };

  return (
    <ScrollView
      contentContainerStyle={{
        padding: 20,
        backgroundColor: '#fff',     // ✅ Light background
        flexGrow: 1,
      }}
    >
      <Text style={{ fontWeight: 'bold', fontSize: 18, color: '#000' }}>
        Earnings Call Summarizer
      </Text>

      <Text style={{ marginTop: 20, color: '#000' }}>Ticker</Text>
      <TextInput
        value={ticker}
        onChangeText={setTicker}
        placeholder="e.g. AAPL"
        placeholderTextColor="#999"
        style={{
          borderWidth: 1,
          padding: 8,
          marginBottom: 10,
          backgroundColor: '#f8f8f8',
          color: '#000',              // ✅ Visible input text
        }}
      />

      <Text style={{ color: '#000' }}>Transcript</Text>
      <TextInput
        value={transcript}
        onChangeText={setTranscript}
        multiline
        numberOfLines={10}
        placeholder="Paste transcript here..."
        placeholderTextColor="#999"
        style={{
          borderWidth: 1,
          padding: 8,
          marginBottom: 10,
          height: 150,
          textAlignVertical: 'top',
          backgroundColor: '#f8f8f8',
          color: '#000',              // ✅ Visible input text
        }}
      />

      <Button title={loading ? 'Summarizing...' : 'Summarize'} onPress={handleSubmit} disabled={loading} />

      {loading && <ActivityIndicator style={{ marginTop: 20 }} />}

      {summary.length > 0 && (
        <>
          <Text style={{ marginTop: 20, fontWeight: 'bold', color: '#000' }}>Summary:</Text>
          <Text style={{ color: '#000' }}>{summary}</Text>
        </>
      )}
    </ScrollView>
  );
}
