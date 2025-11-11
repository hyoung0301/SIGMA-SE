import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, SectionList, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// --- 임시 데이터: SectionList 형식을 따름 ---
const SCHEDULE_DATA = [
  {
    title: '11월 9일 (일)',
    data: [
      { time: '10:00', title: '소프트웨어공학 중간고사', location: '공학관 301호', tag: '시험' },
      { time: '14:00', title: '학과 세미나', location: '대회의실', tag: '세미나' },
    ],
  },
  {
    title: '11월 10일 (월)',
    data: [
      { time: '14:00', title: '데이터베이스 중간고사', location: '공학관 405호', tag: '시험' },
    ],
  },
  {
    title: '11월 13일 (수)',
    data: [
      { time: '09:00', title: '소프트웨어공학 발표', location: '온라인', tag: '수강신청' },
    ],
  },
];

// --- 컴포넌트: 개별 일정 항목 카드 ---
const ScheduleItem = ({ item }) => {
  const getTagStyle = (tag) => {
    switch (tag) {
      case '시험': return { color: '#E91E63', backgroundColor: '#FCE4EC' };
      case '세미나': return { color: '#00BCD4', backgroundColor: '#E0F7FA' };
      case '수강신청': return { color: '#4CAF50', backgroundColor: '#E8F5E9' };
      default: return { color: '#666', backgroundColor: '#EEE' };
    }
  };
  const tagStyle = getTagStyle(item.tag);

  return (
    <TouchableOpacity style={styles.itemCard}>
      <View style={styles.timeWrapper}>
        <Ionicons name="time-outline" size={24} color="#007AFF" />
        <Text style={styles.timeText}>{item.time}</Text>
      </View>
      
      <View style={styles.contentWrapper}>
        <View style={styles.contentHeader}>
          <Text style={styles.itemTitle}>{item.title}</Text>
          <Text style={[styles.itemTag, { backgroundColor: tagStyle.backgroundColor, color: tagStyle.color }]}>
            {item.tag}
          </Text>
        </View>
        <Text style={styles.itemLocation}>{item.location}</Text>
        <Text style={styles.itemTimeRange}>{item.time}-12:00 (임시)</Text> 
      </View>
    </TouchableOpacity>
  );
};

// ✅ Render Error 해결을 위한 필수 요소: export default function
export default function AcademicScheduleScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <SectionList
        sections={SCHEDULE_DATA}
        keyExtractor={(item, index) => item.title + index}
        renderItem={({ item }) => <ScheduleItem item={item} />}
        renderSectionHeader={({ section: { title } }) => (
          <Text style={styles.sectionHeader}>{title}</Text>
        )}
        contentContainerStyle={styles.listContent}
      />
    </SafeAreaView>
  );
}

// --- 스타일 시트 (이전과 동일) ---
const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F7F7F7', },
  listContent: { paddingHorizontal: 20, paddingTop: 10, },
  sectionHeader: { fontSize: 16, fontWeight: 'bold', color: '#333333', marginTop: 20, marginBottom: 10, },
  itemCard: { flexDirection: 'row', backgroundColor: '#FFFFFF', borderRadius: 12, padding: 15, marginBottom: 10, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 3, elevation: 2, },
  timeWrapper: { width: 60, alignItems: 'center', paddingRight: 10, borderRightWidth: 1, borderRightColor: '#EEE', marginRight: 15, },
  timeText: { fontSize: 14, fontWeight: 'bold', color: '#333', marginTop: 5, },
  contentWrapper: { flex: 1, justifyContent: 'center', },
  contentHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3, },
  itemTitle: { fontSize: 16, fontWeight: '600', color: '#000', maxWidth: '80%', },
  itemLocation: { fontSize: 13, color: '#666', marginBottom: 2, },
  itemTimeRange: { fontSize: 12, color: '#999', },
  itemTag: { fontSize: 11, fontWeight: 'bold', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 15, overflow: 'hidden', },
});