import React, { useState } from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, FlatList, TextInput, 
  TouchableOpacity, ScrollView 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// --- 임시 강의 데이터 ---
const COURSE_DATA = [
  { id: '1', title: '소프트웨어공학', code: 'CSE301', professor: '김교수', location: '공학관 301호', capacity: '45/50명', schedule: '월수 10:00-12:00', credits: '3학점', status: '신청가능' },
  { id: '2', title: '데이터베이스', code: 'CSE362', professor: '이교수', location: '공학관 405호', capacity: '50/50명', schedule: '화목 14:00-16:00', credits: '3학점', status: '마감' },
  { id: '3', title: '인공지능', code: 'CSE305', professor: '박교수', location: '공학관 201호', capacity: '38/50명', schedule: '월수 14:00-16:00', credits: '3학점', status: '신청가능' },
  { id: '4', title: '컴퓨터 구조', code: 'CSE202', professor: '최교수', location: '정보관 101호', capacity: '40/40명', schedule: '화목 09:00-11:00', credits: '3학점', status: '마감' },
];

// --- 컴포넌트: 개별 강의 항목 카드 ---
const CourseItem = ({ item }) => {
  const isAvailable = item.status === '신청가능';
  
  const statusStyle = {
    color: isAvailable ? '#4CAF50' : '#E91E63',
    backgroundColor: isAvailable ? '#E8F5E9' : '#FCE4EC',
  };

  return (
    <TouchableOpacity style={styles.itemCard}>
      <View style={styles.cardHeader}>
        <Text style={styles.courseTitle}>{item.title}</Text>
        <Text style={styles.courseCode}>{item.code}</Text>
        <Text style={[styles.statusTag, statusStyle]}>{item.status}</Text>
      </View>

      <Text style={styles.professorText}>
        <Ionicons name="person-outline" size={12} color="#666" /> {item.professor} 교수
      </Text>
      
      <View style={styles.detailRow}>
        <View style={styles.detailGroup}>
          <Text style={styles.detailText}>
            <Ionicons name="location-outline" size={12} color="#666" /> {item.location}
          </Text>
          <Text style={styles.detailText}>
            <Ionicons name="people-outline" size={12} color="#666" /> {item.capacity}
          </Text>
        </View>
        <View style={styles.creditWrapper}>
          <Text style={styles.scheduleText}>{item.schedule}</Text>
          <Text style={styles.creditText}>{item.credits}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

// --- 강의 검색 화면 컴포넌트 ---
export default function CourseSearchScreen() {
  const [searchText, setSearchText] = useState('');

  // 검색 로직 (제목, 교수, 코드 검색)
  const filteredData = COURSE_DATA.filter(course => 
    course.title.includes(searchText) || 
    course.professor.includes(searchText) || 
    course.code.includes(searchText)
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* 검색 입력창 */}
        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color="#999" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="강의명, 교수명, 강의코드 검색..."
            placeholderTextColor="#999"
            value={searchText}
            onChangeText={setSearchText}
          />
        </View>

        {/* 강의 목록 */}
        <FlatList
          data={filteredData}
          renderItem={({ item }) => <CourseItem item={item} />}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <Text style={styles.emptyText}>검색 결과가 없습니다.</Text>
          }
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

  // 검색창 스타일
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginTop: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#EFEFEF',
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 15,
    paddingVertical: 0,
    color: '#333',
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
    alignItems: 'center',
    marginBottom: 5,
  },
  courseTitle: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#000',
    marginRight: 8,
  },
  courseCode: {
    fontSize: 14,
    color: '#999',
    marginRight: 'auto',
  },
  statusTag: {
    fontSize: 12,
    fontWeight: 'bold',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 15,
    overflow: 'hidden',
  },
  
  professorText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginTop: 5,
  },
  detailGroup: {
    // 강의실, 정원 정보를 묶음
  },
  detailText: {
    fontSize: 13,
    color: '#333',
    marginBottom: 3,
  },
  
  creditWrapper: {
    alignItems: 'flex-end',
  },
  scheduleText: {
    fontSize: 13,
    color: '#333',
    marginBottom: 3,
  },
  creditText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  
  emptyText: {
    textAlign: 'center',
    marginTop: 50,
    fontSize: 16,
    color: '#999',
  }
});