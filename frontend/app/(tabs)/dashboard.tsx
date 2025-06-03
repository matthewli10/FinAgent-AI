import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TouchableOpacity, TextInput, Modal } from 'react-native';
import { getAuth } from 'firebase/auth';
import { addToWatchlist, deleteFromWatchlist, fetchYahooFinancePrices } from '../../services/api';
import { Swipeable } from 'react-native-gesture-handler';
import { useRouter } from 'expo-router';

interface WatchlistItem {
  id: number;
  ticker: string;
  added_at: string;
  user_id: number;
}

const DashboardScreen = () => {
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [newTicker, setNewTicker] = useState('');
  const [adding, setAdding] = useState(false);
  const [prices, setPrices] = useState<{ [key: string]: { price: number, change: number, changePercent: number } }>({});

  // Mock price change data for UI
  const mockPriceChange = (ticker: string): string => {
    const changes: { [key: string]: number } = {
      'TSLA': -0.6, 'BA': 1.3, 'TCEHY': 2.8, 'AMD': 0.9, 'NVDA': -1.6, 'MSFT': -0.4
    };
    return changes[ticker.toUpperCase()] !== undefined
      ? changes[ticker.toUpperCase()].toFixed(1)
      : (Math.random() * 4 - 2).toFixed(1);
  };

  const fetchWatchlist = async () => {
    setLoading(true);
    setError(null);
    try {
      const user = getAuth().currentUser;
      if (!user) throw new Error('User not authenticated');
      const token = await user.getIdToken();
      const res = await fetch('http://192.168.86.45:8000/watchlist', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) throw new Error('Failed to fetch watchlist');
      const data = await res.json();
      setWatchlist(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrices = async (tickers: string[]) => {
    try {
      const priceData = await fetchYahooFinancePrices(tickers);
      console.log('yfinance data:', priceData);
      setPrices(priceData as { [key: string]: { price: number, change: number, changePercent: number } });
    } catch (err) {
      console.error('yfinance error:', err);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  useEffect(() => {
    if (watchlist.length > 0) {
      fetchPrices(watchlist.map(item => item.ticker));
    }
  }, [watchlist]);

  const handleAddStock = async () => {
    if (!newTicker.trim()) return;
    setAdding(true);
    try {
      const user = getAuth().currentUser;
      if (!user) throw new Error('User not authenticated');
      const token = await user.getIdToken();
      await addToWatchlist(newTicker.trim().toUpperCase(), token);
      setNewTicker('');
      setModalVisible(false);
      fetchWatchlist();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (ticker: string) => {
    try {
      const user = getAuth().currentUser;
      if (!user) throw new Error('User not authenticated');
      const token = await user.getIdToken();
      await deleteFromWatchlist(ticker, token);
      fetchWatchlist();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleStockPress = (ticker: string) => {
    router.push(`/stock/${ticker}`);
  };

  const renderRightActions = (ticker: string) => (
    <View style={styles.rowBack}>
      <TouchableOpacity style={styles.deleteButton} onPress={() => handleDelete(ticker)}>
        <Text style={styles.deleteButtonText}>Delete</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#00bfff" /></View>;
  }
  if (error) {
    return <View style={styles.center}><Text style={styles.error}>{error}</Text></View>;
  }

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.header}>Watchlist</Text>
        <TouchableOpacity style={styles.addButton} onPress={() => setModalVisible(true)}>
          <Text style={styles.addButtonText}>＋</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={watchlist}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => {
          const priceInfo = prices[item.ticker.toUpperCase()];
          const priceChange = priceInfo ? priceInfo.changePercent.toFixed(1) : '--';
          const isPositive = priceInfo ? priceInfo.changePercent > 0 : false;
          return (
            <Swipeable renderRightActions={() => renderRightActions(item.ticker)}>
              <TouchableOpacity 
                style={styles.stockRow}
                onPress={() => handleStockPress(item.ticker)}
              >
                <Text style={styles.ticker}>{item.ticker}</Text>
                <View style={styles.miniChart} />
                <View style={[styles.badge, { backgroundColor: isPositive ? '#1ecb7b' : '#ff4d4f' }] }>
                  <Text style={styles.badgeText}>{priceInfo ? (isPositive ? '+' : '') + priceChange + '%' : '--'}</Text>
                </View>
                <Text style={styles.priceText}>{priceInfo ? `$${priceInfo.price.toFixed(2)}` : '--'}</Text>
              </TouchableOpacity>
            </Swipeable>
          );
        }}
        contentContainerStyle={{ paddingBottom: 20 }}
      />
      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add Stock</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter Ticker (e.g. TSLA)"
              value={newTicker}
              onChangeText={setNewTicker}
              autoCapitalize="characters"
            />
            <TouchableOpacity style={styles.modalButton} onPress={handleAddStock} disabled={adding}>
              <Text style={styles.modalButtonText}>{adding ? 'Adding...' : 'Add'}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setModalVisible(false)}>
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#181A20',
    paddingTop: 40,
    paddingHorizontal: 16,
  },
  header: {
    color: '#00bfff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#23263A',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    flexDirection: 'column',
    alignItems: 'flex-start',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 2,
  },
  ticker: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  chartPlaceholder: {
    width: '100%',
    height: 40,
    backgroundColor: '#2D3250',
    borderRadius: 8,
    marginBottom: 8,
  },
  date: {
    color: '#aaa',
    fontSize: 14,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#181A20',
  },
  error: {
    color: 'red',
    fontSize: 18,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  addButton: {
    backgroundColor: '#23263A',
    borderRadius: 20,
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  addButtonText: {
    color: '#00bfff',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: -2,
  },
  stockRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#23263A',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  miniChart: {
    flex: 1,
    height: 32,
    marginHorizontal: 12,
    backgroundColor: '#2D3250',
    borderRadius: 8,
  },
  badge: {
    minWidth: 56,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#23263A',
    borderRadius: 16,
    padding: 24,
    width: '80%',
    alignItems: 'center',
  },
  modalTitle: {
    color: '#00bfff',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  input: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    width: '100%',
    marginBottom: 16,
    fontSize: 16,
  },
  modalButton: {
    backgroundColor: '#00bfff',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 24,
    marginBottom: 8,
  },
  modalButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  cancelText: {
    color: '#aaa',
    marginTop: 8,
    fontSize: 16,
  },
  priceText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 12,
  },
  rowBack: {
    alignItems: 'center',
    backgroundColor: '#ff4d4f',
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'flex-end',
    borderRadius: 16,
    marginBottom: 12,
    paddingRight: 20,
  },
  deleteButton: {
    backgroundColor: '#ff4d4f',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  deleteButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default DashboardScreen; 