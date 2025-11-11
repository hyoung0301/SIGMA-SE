import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, FlatList, TouchableOpacity } from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';

// --- 임시 시설 데이터 ---
const FACILITY_DATA = [
  { id: '1', name: '중앙도서관', location: '본관 1층', current: 245, total: 300, hours: '09:00-22:00' },
  { id: '2', name: '학생식당', location: '학생회관 지하 1층', current: 180, total: 200, hours: '11:30-19:00' },
  { id: '3', name: '컴퓨터실습실', location: '공학관 3층', current: 45, total: 50, hours: '09:00-21:00' },
  { id: '4', name: '체육관', location: '체육관 1층', current: 5, total: 200, hours: '06:00-23:00' },
];

// --- 컴포넌트: 개별 시설 현황 카드 ---
const FacilityItem = ({ item }) => {
  const usageRate = item.current / item.total;
  let statusText = '';
  let statusColor = '';

  if (usageRate < 0.3) {
    statusText = '여유';
    statusColor = '#4CAF50'; // Green
  } else if (usageRate < 0.8) {
    statusText = '보통';
    statusColor = '#FFC107'; // Yellow
  } else {
    statusText = '혼잡';
    statusColor = '#E91E63'; // Red
  }

  return (
    <TouchableOpacity style={styles.itemCard}>
      <View style={styles.cardHeader}>
        <Text style={styles.facilityTitle}>{item.name}</Text>
        <Text style={[styles.statusTag, { backgroundColor: statusColor + '20', color: statusColor }]}>
          {statusText}
        </Text>
      </View>

      <View style={styles.detailRow}>
        <Text style={styles.detailText}>
          <Ionicons name="location-outline" size={14} color="#666" /> {item.location}
        </Text>
      </View>

      <View style={styles.statusRow}>
        <Text style={styles.detailText}>
          <MaterialCommunityIcons name="account-group-outline" size={14} color="#666" /> 이용 현황
        </Text>
        <Text style={styles.countText}>
          {item.current}/{item.total}명
        </Text>
      </View>

      {/* 이용 현황 ProgressBar */}
      <View style={styles.progressBarBackground}>
        <View style={[styles.progressBarFill, { width: `${usageRate * 100}%`, backgroundColor: statusColor }]} />
      </View>

      <View style={styles.hoursRow}>
        <Text style={styles.detailText}>
          <Ionicons name="time-outline" size={14} color="#666" /> {item.hours}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

// --- 시설 현황 화면 컴포넌트 ---
export default function FacilityStatusScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* 설명 문구 */}
        <Text style={styles.updateText}>
          실시간 업데이트 (1분 단위)
        </Text>
        
        {/* 시설 목록 */}
        <FlatList
          data={FACILITY_DATA}
          renderItem={({ item }) => <FacilityItem item={item} />}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      </View>
    </SafeAreaView>
  );
}

// --- 스타일 시트 ---
const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F7F7F7',
  },
  container: {
    flex: 1,
    paddingHorizontal: 20,
  },
  updateText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    paddingVertical: 10,
    marginBottom: 5,
    fontWeight: '500',
  },

  listContent: {
    paddingBottom: 20,
  },
  
  // 카드 스타일
  itemCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },

  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  facilityTitle: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#000',
  },
  statusTag: {
    fontSize: 12,
    fontWeight: 'bold',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 15,
    overflow: 'hidden',
  },

  detailRow: {
    marginBottom: 10,
  },
  detailText: {
    fontSize: 14,
    color: '#333',
  },
  
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  countText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#000',
  },

  // Progress Bar 스타일
  progressBarBackground: {
    height: 8,
    backgroundColor: '#EFEFEF',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 10,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  
  hoursRow: {
    marginTop: 5,
  }
});