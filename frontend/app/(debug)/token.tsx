import React, { useEffect } from 'react';
import { View, Text } from 'react-native';
import { getAuth } from 'firebase/auth';

export default function TokenLogger() {
  useEffect(() => {
    const fetchDetails = async () => {
      const user = getAuth().currentUser;
      if (!user) {
        console.error("User not logged in");
        return;
      }

      const token = await user.getIdToken();
      console.log("🔥 Firebase token:", token); // ← COPY THIS TOKEN
    };

    fetchDetails();
  }, []);

  return (
    <View>
      <Text>Token logging... check the console.</Text>
    </View>
  );
}
