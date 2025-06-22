const API_BASE_URL = "http://192.168.1.9:8000";

export async function summarizeTranscript(ticker, transcript_text) {
    try {
      const res = await fetch(`${API_BASE_URL}/summarize/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, transcript_text }),
      });
  
      console.log("Status:", res.status);
  
      if (!res.ok) {
        const errorText = await res.text();
        console.error("API Error Response:", errorText);
        throw new Error("API call failed");
      }
  
      return await res.json();
    } catch (err) {
      console.error("Error:", err.message);
      return null;
    }
  }
  
export async function getWatchlist(token) {
    const res = await fetch(`${API_BASE_URL}/watchlist`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || 'Failed to fetch watchlist');
    }
    return await res.json();
}

export async function addToWatchlist(ticker, token) {
  try {
    const res = await fetch(`${API_BASE_URL}/watchlist`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ ticker }),
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || 'Failed to add to watchlist');
    }
    return await res.json();
  } catch (err) {
    throw err;
  }
}

export async function deleteFromWatchlist(ticker, token) {
  try {
    const res = await fetch(`${API_BASE_URL}/watchlist/${ticker}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || 'Failed to delete from watchlist');
    }
    return await res.json();
  } catch (err) {
    throw err;
  }
}

export async function fetchYahooFinancePrices(tickers) {
  const symbols = tickers.join(',');
  const url = `${API_BASE_URL}/stock-prices?symbols=${symbols}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch prices');
    const data = await res.json();
    // Data is already in the correct format: { TICKER: { price, change, changePercent } }
    return data;
  } catch (err) {
    throw err;
  }
}

export async function fetchStockDetails(ticker, token) {
  const response = await fetch(`${API_BASE_URL}/stock/${ticker}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch stock details');
  }

  return response.json();
}
  