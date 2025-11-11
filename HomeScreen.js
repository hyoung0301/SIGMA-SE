import React, { useLayoutEffect } from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, TouchableOpacity, Image, ScrollView 
} from 'react-native';
import { MaterialCommunityIcons, Ionicons } from '@expo/vector-icons'; 

const SIGMA_LOGO = 'https://via.placeholder.com/40x40/000033/FFFFFF?text=S'; 

const FeatureCard = ({ iconName, iconColor, title, onPress }) => (
  <TouchableOpacity style={styles.featureCard} onPress={onPress}>
    <View style={[styles.iconContainer, { borderColor: iconColor }]}>
      <MaterialCommunityIcons name={iconName} size={30} color={iconColor} />
    </View>
    <Text style={styles.featureText}>{title}</Text>
  </TouchableOpacity>
);

// ✅ 프로필 버튼 컴포넌트
const ProfileButton = ({ navigation }) => (
  <TouchableOpacity
    onPress={() => navigation.navigate('Profile')} // 'Profile' 화면으로 이동
    style={{ marginRight: 10 }}
  >
    <Ionicons name="person-circle-outline" size={30} color="#000033" />
  </TouchableOpacity>
);


export default function HomeScreen({ navigation }) {
  
  // 🚨 네비게이션 헤더에 프로필 버튼을 설정합니다.
  useLayoutEffect(() => {
    navigation.setOptions({
      headerShown: true, // App.js에서 true로 설정했지만, 여기서 커스텀을 위해 다시 명시
      headerTitle: '', // 제목은 빈칸으로 둡니다.
      headerStyle: {
        backgroundColor: '#FFFFFF', // 배경색 지정
        elevation: 0, // 안드로이드 그림자 제거
        shadowOpacity: 0, // iOS 그림자 제거
        height: 50 // 헤더 높이 설정
      },
      // 오른쪽 헤더 버튼을 ProfileButton 컴포넌트로 지정
      headerRight: () => <ProfileButton navigation={navigation} />,
      // 왼쪽 헤더 버튼은 비워둡니다 (메인 화면이므로 뒤로가기 버튼 없음)
      headerLeft: () => null,
    });
  }, [navigation]); 

  
  const handleFeaturePress = (screenName) => {
    if (screenName === 'Chat') {
      navigation.navigate('Chat'); 
    } else if (screenName === 'AcademicSchedule') { 
      navigation.navigate('AcademicSchedule'); 
    } else if (screenName === 'CourseSearch') { 
      navigation.navigate('CourseSearch'); 
    } else if (screenName === 'FacilityStatus') {
      navigation.navigate('FacilityStatus'); 
    } else if (screenName === 'FAQ') { 
      navigation.navigate('FAQ'); 
    } else {
      alert(`${screenName} 화면은 아직 구현되지 않았습니다.`); 
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.container}>

          {/* 1. 로고 및 제목 영역 */}
          <View style={styles.header}>
            <Image source={{ uri: SIGMA_LOGO }} style={styles.logo} resizeMode="contain" />
            <Text style={styles.logoText}>SIGMA</Text>
          </View>
          <Text style={styles.subTitle}>캠퍼스 AI 어시스턴트</Text>

          {/* 2. AI 대화 시작 영역 */}
          <View style={styles.chatBox}>
            <Text style={styles.chatTitle}>무엇이든 물어보세요!</Text>
            <Text style={styles.chatSubText}>학사 일정부터 시설 정보까지 궁금한 모든 것을 도와드립니다.</Text>
            <TouchableOpacity 
              style={styles.chatButton} 
              onPress={() => handleFeaturePress('Chat')} 
            >
              <Ionicons name="chatbubbles-outline" size={18} color="#FFFFFF" style={{ marginRight: 8 }} />
              <Text style={styles.chatButtonText}>대화 시작하기</Text>
            </TouchableOpacity>
          </View>

          {/* 3. 주요 기능 섹션 */}
          <Text style={styles.sectionTitle}>주요 기능</Text>
          <View style={styles.featuresGrid}>
            {[
              { id: 1, name: '학사 일정 조회 및 등록', icon: 'calendar-clock', color: '#6A7DFF', screen: 'AcademicSchedule' }, 
              { id: 2, name: '강의 및 수업 정보 검색', icon: 'book-open-page-variant', color: '#4CAF50', screen: 'CourseSearch' },
              { id: 3, name: '실시간 시설 현황 조회', icon: 'clock-time-three-outline', color: '#9C27B0', screen: 'FacilityStatus' },
              { id: 4, name: 'FAQ', icon: 'help-circle-outline', color: '#FF9800', screen: 'FAQ' },
            ].map(item => (
              <FeatureCard 
                key={item.id}
                iconName={item.icon}
                iconColor={item.color}
                title={item.name}
                onPress={() => handleFeaturePress(item.screen)}
              />
            ))}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// --- 스타일 시트 ---
const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF', },
  scrollContent: { flexGrow: 1, },
  container: { paddingHorizontal: 20, paddingBottom: 20, },
  // 헤더 컴포넌트가 헤더 영역을 차지하지 않도록 marginTop을 조정할 수 있습니다.
  header: { flexDirection: 'row', alignItems: 'center', marginTop: 10, marginBottom: 5, }, 
  logo: { width: 40, height: 40, },
  logoText: { fontSize: 24, fontWeight: 'bold', marginLeft: 10, color: '#000033', },
  subTitle: { fontSize: 18, color: '#333333', marginBottom: 30, fontWeight: '500', },
  chatBox: { backgroundColor: '#F3F4F6', borderRadius: 15, padding: 20, alignItems: 'center', marginBottom: 30, },
  chatTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 5, color: '#000000', },
  chatSubText: { fontSize: 14, color: '#666666', textAlign: 'center', marginBottom: 20, },
  chatButton: { backgroundColor: '#007AFF', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, paddingHorizontal: 30, borderRadius: 25, width: '100%', },
  chatButtonText: { color: '#FFFFFF', fontSize: 16, fontWeight: 'bold', },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#555555', marginBottom: 15, },
  featuresGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', },
  featureCard: { width: '48%', height: 140, backgroundColor: '#FFFFFF', borderRadius: 15, padding: 15, marginBottom: 15, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3, justifyContent: 'space-between', },
  iconContainer: { width: 50, height: 50, borderRadius: 10, borderWidth: 2, alignItems: 'center', justifyContent: 'center', marginBottom: 10, },
  featureText: { fontSize: 14, fontWeight: '500', color: '#333333', },
});