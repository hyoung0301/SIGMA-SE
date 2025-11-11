// App.js 파일

import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native'; 
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // 🚨 이 줄을 꼭 확인하세요!

// 🚨 경로 확인: 현재 폴더 구조에 맞게 경로를 설정합니다. (src/screens 기준)
import HomeScreen from './src/screens/HomeScreen.js'; 
import ChatScreen from './src/screens/ChatScreen.js'; 
import AcademicScheduleScreen from './src/screens/AcademicScheduleScreen.js'; 
import CourseSearchScreen from './src/screens/CourseSearchScreen.js'; 
import FacilityStatusScreen from './src/screens/FacilityStatusScreen.js'; 
import FAQScreen from './src/screens/FAQScreen.js'; 

// 새 인증 관련 화면 추가
import LoginScreen from './src/screens/LoginScreen.js'; 
import SignUpScreen from './src/screens/SignUpScreen.js'; 
import ProfileScreen from './src/screens/ProfileScreen.js'; 

// 🚨 이 부분이 import 바로 다음에 위치해야 합니다!
const Stack = createNativeStackNavigator(); 

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Login" 
      >
        {/* 0. 인증 화면 (메인 기능보다 먼저 배치) */}
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name="SignUp" 
          component={SignUpScreen} 
          options={{ title: '회원가입', headerTitleAlign: 'center' }} 
        />
        <Stack.Screen 
          name="Profile" 
          component={ProfileScreen} 
          options={{ title: '내 정보', headerTitleAlign: 'center' }} 
        />

        {/* 1. 메인 화면 */}
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ headerShown: true }} 
        />
        
        {/* 2. AI 채팅 화면 */}
        <Stack.Screen 
          name="Chat" 
          component={ChatScreen} 
          options={{ headerShown: false }} 
        />
        
        {/* 3. 학사 일정 화면 */}
        <Stack.Screen 
          name="AcademicSchedule" 
          component={AcademicScheduleScreen} 
          options={{ title: '학사 일정', headerTitleAlign: 'center' }} 
        />
        
        {/* 4. 강의 검색 화면 */}
        <Stack.Screen 
          name="CourseSearch" 
          component={CourseSearchScreen} 
          options={{ title: '강의 정보', headerTitleAlign: 'center' }} 
        />
        
        {/* 5. 시설 현황 화면 */}
        <Stack.Screen 
          name="FacilityStatus" 
          component={FacilityStatusScreen} 
          options={{ title: '시설 현황', headerTitleAlign: 'center' }} 
        />
        
        {/* 6. FAQ 화면 */}
        <Stack.Screen 
          name="FAQ" 
          component={FAQScreen} 
          options={{ title: '자주 묻는 질문', headerTitleAlign: 'center' }} 
        />
        
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default App;