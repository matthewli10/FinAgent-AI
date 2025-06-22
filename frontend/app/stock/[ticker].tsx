import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { getAuth } from 'firebase/auth';
import { fetchStockDetails } from '../../services/api.js';

interface StockDetails {
  price: number;
  change: number;
  changePercent: number;
  marketCap: number;
  peRatio: number;
  eps: number;
  volume: number;
  summary: string;
}

export default function StockDetailsScreen() {
  const { ticker } = useLocalSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stockDetails, setStockDetails] = useState<StockDetails | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  useEffect(() => {
    const getDetails = async () => {
      try {
        setLoading(true);
        const user = getAuth().currentUser;
        if (!user) throw new Error('User not authenticated');
        const token = await user.getIdToken();
        const details = await fetchStockDetails(ticker as string, token);
        setStockDetails(details);
        
        stopPolling();

        if (details.summary === "generating...") {
          pollingIntervalRef.current = setInterval(async () => {
            try {
              console.log(`Polling for ${ticker} summary...`);
              const updatedDetails = await fetchStockDetails(ticker as string, token);
              if (updatedDetails.summary !== "generating...") {
                setStockDetails(updatedDetails);
                stopPolling();
              }
            } catch (pollError) {
              console.error("Polling failed:", pollError);
              setError("Failed to retrieve summary.");
              stopPolling();
            }
          }, 5000);
        }
      } catch (err: any) {
        setError(err.message);
        stopPolling();
      } finally {
        setLoading(false);
      }
    };

    getDetails();

    return () => stopPolling();
  }, [ticker]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#00bfff" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }

  if (!stockDetails) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>No data available</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.ticker}>{ticker}</Text>
        <Text style={styles.price}>${stockDetails.price.toFixed(2)}</Text>
        <View style={[styles.badge, { backgroundColor: stockDetails.changePercent > 0 ? '#1ecb7b' : '#ff4d4f' }]}>
          <Text style={styles.badgeText}>
            {stockDetails.changePercent > 0 ? '+' : ''}{stockDetails.changePercent.toFixed(1)}%
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Key Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Market Cap</Text>
            <Text style={styles.statValue}>${(stockDetails.marketCap / 1e9).toFixed(2)}B</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>P/E Ratio</Text>
            <Text style={styles.statValue}>{stockDetails.peRatio.toFixed(2)}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>EPS</Text>
            <Text style={styles.statValue}>${stockDetails.eps.toFixed(2)}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Volume</Text>
            <Text style={styles.statValue}>{(stockDetails.volume / 1000).toFixed(0)}K</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Analysis</Text>
        <View style={styles.summaryCard}>
          {stockDetails.summary === "generating..." ? (
            <View style={styles.generatingContainer}>
              <ActivityIndicator color="#00bfff" />
              <Text style={styles.generatingText}>AI analysis in progress...</Text>
            </View>
          ) : (
            <Text style={styles.summaryText}>{stockDetails.summary}</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#181A20',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#181A20',
  },
  header: {
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#23263A',
  },
  ticker: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  price: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  badgeText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    backgroundColor: '#23263A',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  statLabel: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 4,
  },
  statValue: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  summaryCard: {
    backgroundColor: '#23263A',
    padding: 16,
    borderRadius: 12,
  },
  summaryText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 24,
  },
  error: {
    color: '#ff4d4f',
    fontSize: 16,
  },
  generatingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  generatingText: {
    color: '#00bfff',
    marginLeft: 10,
    fontSize: 16,
  },
}); 