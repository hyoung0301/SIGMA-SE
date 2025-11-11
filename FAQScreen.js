import React, { useState } from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, FlatList, TextInput, 
  TouchableOpacity, ScrollView 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// --- 임시 FAQ 데이터 ---
const FAQ_CATEGORIES = [
  { name: '학사 일정', count: 12, color: '#6A7DFF' },
  { name: '수강 신청', count: 15, color: '#4CAF50' },
  { name: '등록금', count: 8, color: '#9C27B0' },
  { name: '장학금', count: 10, color: '#FF9800' },
];

const FAQ_DATA = [
  { id: '1', category: '수강 신청', question: '수강 신청은 언제 시작하나요?', answer: '수강 신청은 매 학기 직전 공지되는 학사 일정에 따라 진행됩니다. 자세한 날짜는 학사 일정 메뉴를 확인해 주세요.' },
  { id: '2', category: '학사 일정', question: '중간고사 일정은 어떻게 되나요?', answer: '중간고사 및 기말고사 일정은 개강 후 4주 이내에 학과 공지사항 및 학사 일정 메뉴를 통해 확인 가능합니다.' },
  { id: '3', category: '장학금', question: '성적 장학금 신청 방법을 알려주세요', answer: '성적 장학금은 별도 신청 없이 성적 기준에 따라 자동 선발됩니다.' },
  { id: '4', category: '등록금', question: '등록금 납부 기간을 놓쳤는데 어떻게 해야 하나요?', answer: '등록금 납부 기간 이후에는 추가 납부 기간에만 납부 가능합니다. 교무과에 문의하세요.' },
  { id: '5', category: '수강 신청', question: '수강 인원이 초과된 강의를 들을 수 있나요?', answer: '수강 인원 초과 시에는 교수님의 재량에 따라 추가 인원 신청이 가능할 수도 있습니다.' },
];

// --- 컴포넌트: 카테고리 버튼 ---
const CategoryPill = ({ category, isSelected, onPress }) => (
  <TouchableOpacity 
    style={[styles.categoryPill, isSelected && styles.categoryPillSelected]}
    onPress={() => onPress(category.name)}
  >
    <Text style={styles.categoryText}>{category.name}</Text>
    <Text style={[styles.categoryCount, { backgroundColor: category.color + '20', color: category.color }]}>
      {category.count}
    </Text>
  </TouchableOpacity>
);

// --- 컴포넌트: 질문 항목 ---
const QuestionItem = ({ item }) => (
  <TouchableOpacity style={styles.questionItem}>
    <Text style={[styles.questionCategory, { color: FAQ_CATEGORIES.find(c => c.name === item.category)?.color || '#999' }]}>
      {item.category}
    </Text>
    <Text style={styles.questionText}>{item.question}</Text>
    <Ionicons name="chevron-forward-outline" size={20} color="#AAAAAA" />
  </TouchableOpacity>
);

// --- FAQ 화면 컴포넌트 ---
export default function FAQScreen() {
  const [searchText, setSearchText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('전체');

  // 데이터 필터링 로직
  const filteredData = FAQ_DATA.filter(item => {
    const categoryMatch = selectedCategory === '전체' || item.category === selectedCategory;
    const searchMatch = item.question.includes(searchText) || item.answer.includes(searchText);
    return categoryMatch && searchMatch;
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.container}>

          {/* 검색 입력창 */}
          <View style={styles.searchContainer}>
            <Ionicons name="search" size={20} color="#999" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="궁금한 내용을 검색하세요..."
              placeholderTextColor="#999"
              value={searchText}
              onChangeText={setSearchText}
            />
          </View>

          {/* 카테고리 필터 */}
          <Text style={styles.sectionTitle}>카테고리</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryScroll}>
            <CategoryPill 
              category={{ name: '전체', count: FAQ_DATA.length, color: '#000' }} 
              isSelected={selectedCategory === '전체'}
              onPress={() => setSelectedCategory('전체')}
            />
            {FAQ_CATEGORIES.map(cat => (
              <CategoryPill
                key={cat.name}
                category={cat}
                isSelected={selectedCategory === cat.name}
                onPress={setSelectedCategory}
              />
            ))}
          </ScrollView>
          
          {/* 질문 목록 */}
          <Text style={styles.sectionTitle}>
            {selectedCategory === '전체' ? '전체 질문' : `${selectedCategory} 질문`}
          </Text>
          
          {filteredData.length > 0 ? (
            <FlatList
              data={filteredData}
              renderItem={({ item }) => <QuestionItem item={item} />}
              keyExtractor={(item) => item.id}
              scrollEnabled={false} // ScrollView 안에 있으므로 비활성화
              ItemSeparatorComponent={() => <View style={styles.separator} />}
            />
          ) : (
            <Text style={styles.emptyText}>'{searchText}'에 대한 검색 결과가 없습니다.</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// --- 스타일 시트 ---
const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF', },
  scrollContent: { paddingBottom: 30, },
  container: { paddingHorizontal: 20, paddingTop: 10, },
  
  // 검색창 스타일
  searchContainer: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F3F4F6', borderRadius: 10, paddingHorizontal: 15, paddingVertical: 10, marginBottom: 20, },
  searchIcon: { marginRight: 10, },
  searchInput: { flex: 1, fontSize: 15, paddingVertical: 0, color: '#333', },
  
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#333', marginTop: 15, marginBottom: 10, },
  
  // 카테고리 필터 스타일
  categoryScroll: { marginBottom: 15, },
  categoryPill: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F3F4F6', borderRadius: 20, paddingHorizontal: 15, paddingVertical: 8, marginRight: 8, },
  categoryPillSelected: { backgroundColor: '#E0E0FF', borderWidth: 1, borderColor: '#6A7DFF' },
  categoryText: { fontSize: 14, color: '#333', fontWeight: '500', marginRight: 5, },
  categoryCount: { fontSize: 12, fontWeight: 'bold', paddingHorizontal: 6, paddingVertical: 1, borderRadius: 10, overflow: 'hidden', },
  
  // 질문 항목 스타일
  questionItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 15, },
  questionCategory: { fontSize: 12, fontWeight: 'bold', marginRight: 10, },
  questionText: { flex: 1, fontSize: 16, color: '#000', fontWeight: '500', },
  separator: { height: 1, backgroundColor: '#EEEEEE', },
  emptyText: { textAlign: 'center', marginTop: 30, fontSize: 16, color: '#999', },
});