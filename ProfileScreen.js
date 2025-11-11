import React from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, TouchableOpacity, ScrollView 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// --- 임시 사용자 데이터 ---
const USER_DATA = {
  name: '홍길동',
  studentId: '20231234',
  major: '컴퓨터공학과',
  gpa: 3.8,
  credits: 42,
  year: 2,
};

// --- 임시 앱 사용 데이터 ---
const USAGE_DATA = {
  chats: 24,
  questions: 18,
  avgResponseTime: '2.3초',
};

// --- 컴포넌트: 설정 항목 ---
const SettingItem = ({ iconName, title, onPress }) => (
  <TouchableOpacity style={styles.settingItem} onPress={onPress}>
    <Ionicons name={iconName} size={24} color="#666" />
    <Text style={styles.settingText}>{title}</Text>
    <Ionicons name="chevron-forward-outline" size={20} color="#AAAAAA" />
  </TouchableOpacity>
);

export default function ProfileScreen({ navigation }) {
  const handleLogout = () => {
    // 임시 로그아웃 로직: 로그인 화면으로 돌아가기
    navigation.navigate('Login');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.container}>
          
          {/* 사용자 정보 섹션 */}
          <View style={styles.userInfoBox}>
            <View style={styles.nameRow}>
              <Text style={styles.userName}>{USER_DATA.name}</Text>
              <Text style={styles.userId}>{USER_DATA.studentId}</Text>
            </View>
            <Text style={styles.userMajor}>{USER_DATA.major}</Text>
            
            <View style={styles.statsRow}>
              <View style={styles.statPill}><Text style={styles.statLabel}>평점</Text><Text style={styles.statValue}>{USER_DATA.gpa}</Text></View>
              <View style={styles.statPill}><Text style={styles.statLabel}>학점</Text><Text style={styles.statValue}>{USER_DATA.credits}</Text></View>
              <View style={styles.statPill}><Text style={styles.statLabel}>학년</Text><Text style={styles.statValue}>{USER_DATA.year}학년</Text></View>
            </View>
          </View>
          
          {/* 이번 주 SIGMA 사용 섹션 */}
          <Text style={styles.sectionTitle}>이번 주 SIGMA 사용</Text>
          <View style={styles.usageBox}>
            <View style={styles.usageItem}>
              <Text style={styles.usageValue}>{USAGE_DATA.chats}회</Text>
              <Text style={styles.usageLabel}>대화 횟수</Text>
            </View>
            <View style={styles.usageItem}>
              <Text style={styles.usageValue}>{USAGE_DATA.questions}개</Text>
              <Text style={styles.usageLabel}>질문 수</Text>
            </View>
            <View style={styles.usageItem}>
              <Text style={styles.usageValue}>{USAGE_DATA.avgResponseTime}</Text>
              <Text style={styles.usageLabel}>평균 응답 시간</Text>
            </View>
          </View>
          
          {/* 설정 섹션 */}
          <Text style={styles.sectionTitle}>설정</Text>
          <View style={styles.settingsGroup}>
            <SettingItem iconName="person-outline" title="프로필 수정" onPress={() => {}} />
            <SettingItem iconName="notifications-outline" title="알림 설정" onPress={() => {}} />
            <SettingItem iconName="settings-outline" title="환경 설정" onPress={() => {}} />
            <SettingItem iconName="log-out-outline" title="로그아웃" onPress={handleLogout} />
          </View>

        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F7F7F7' },
  scrollView: { flex: 1, },
  container: { paddingHorizontal: 20, paddingTop: 10, paddingBottom: 30, },
  
  // 사용자 정보 섹션
  userInfoBox: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: 20, marginBottom: 20, },
  nameRow: { flexDirection: 'row', alignItems: 'flex-end', marginBottom: 5, },
  userName: { fontSize: 24, fontWeight: 'bold', color: '#000', marginRight: 10, },
  userId: { fontSize: 16, color: '#666', marginBottom: 2, },
  userMajor: { fontSize: 15, color: '#333', marginBottom: 15, },
  
  statsRow: { flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderTopColor: '#EEEEEE', paddingTop: 15, },
  statPill: { alignItems: 'center', flex: 1, },
  statLabel: { fontSize: 13, color: '#999', marginBottom: 3, },
  statValue: { fontSize: 18, fontWeight: 'bold', color: '#007AFF', },

  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#333', marginTop: 20, marginBottom: 10, },
  
  // 사용량 섹션
  usageBox: { backgroundColor: '#FFFFFF', borderRadius: 12, padding: 20, flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20, },
  usageItem: { alignItems: 'center', flex: 1, },
  usageValue: { fontSize: 18, fontWeight: 'bold', color: '#000', marginBottom: 3, },
  usageLabel: { fontSize: 13, color: '#666', },

  // 설정 섹션
  settingsGroup: { backgroundColor: '#FFFFFF', borderRadius: 12, },
  settingItem: { flexDirection: 'row', alignItems: 'center', padding: 15, borderBottomWidth: 1, borderBottomColor: '#EEEEEE', },
  settingText: { flex: 1, fontSize: 16, color: '#333', marginLeft: 15, },
});