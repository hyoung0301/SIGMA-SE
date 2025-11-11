import React, { useState } from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, TextInput, 
  TouchableOpacity, Alert, KeyboardAvoidingView, Platform
} from 'react-native';

const BASE_URL = "https://melina-unrequested-stacee.ngrok-free.dev"; 


export default function LoginScreen({ navigation }) {
  const [studentId, setStudentId] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    // 1-1. 유효성 검사
    if (!studentId || !password) {
      Alert.alert('오류', '학번과 비밀번호를 모두 입력해 주세요.');
      return;
    }

    try {
      // 1-2. API 요청 (POST /auth/login)
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          studentId: studentId,
          password: password,
        }),
      });

      // 1-3. 응답 처리
      if (response.ok) {
        // ✅ 로그인 성공 (HTTP 200-299)
        const data = await response.json(); 
        
        // 실제 앱에서는 여기서 JWT 토큰을 저장해야 합니다.
        
        Alert.alert('로그인 성공', '환영합니다!');
        
        // 다음 화면(예: Home)으로 이동
        navigation.replace('Home'); 
        
      } else {
        // ❌ 서버 측 오류 (HTTP 4xx, 5xx)
        let message = `로그인 실패 (HTTP 상태 코드: ${response.status}).`;

        // 🚨 401 에러 처리: 학번 혹은 비밀번호 오류 메시지 출력
        if (response.status === 401) {
            message = "⚠️ 학번 혹은 비밀번호가 잘못되었습니다.";
        } else {
            // 그 외의 에러 처리 (JSON 파싱 시도)
            let serverResponseText = '';
            try {
                serverResponseText = await response.text();
                const errorData = JSON.parse(serverResponseText); 
                message = errorData.message || errorData.error || message;
            } catch (e) {
                if (serverResponseText.length > 0 && serverResponseText.length < 50) {
                     message += ` 서버 응답 본문: ${serverResponseText}`;
                }
                console.error('로그인 응답 파싱 실패:', e, '서버 텍스트:', serverResponseText);
            }
        }
        
        Alert.alert('로그인 실패', message);
      }
    } catch (error) {
      // 🚨 네트워크 오류 (서버 연결 불가)
      console.error('로그인 통신 오류:', error);
      Alert.alert(
        '네트워크 오류', 
        '서버에 연결할 수 없습니다. ngrok과 백엔드 서버가 실행 중인지 확인해 주세요.'
      );
    }
  };

  return (
    <KeyboardAvoidingView 
        style={styles.safeArea} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.container}>
          
          <Text style={styles.logoText}>SIGMA</Text>
          <Text style={styles.subText}>캠퍼스 AI 어시스턴트</Text>

          <View style={styles.inputGroup}>
            <TextInput 
              style={styles.input} 
              placeholder="학번" 
              keyboardType="numeric" 
              value={studentId} 
              onChangeText={setStudentId} 
            />
            <TextInput 
              style={styles.input} 
              placeholder="비밀번호" 
              secureTextEntry 
              value={password} 
              onChangeText={setPassword} 
            />
          </View>

          <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
            <Text style={styles.loginButtonText}>로그인</Text>
          </TouchableOpacity>

          <View style={styles.linkContainer}>
            <TouchableOpacity onPress={() => navigation.navigate('SignUp')}>
              <Text style={styles.linkText}>회원가입</Text>
            </TouchableOpacity>
            <Text style={styles.separator}>|</Text>
            <TouchableOpacity onPress={() => Alert.alert('기능 구현 예정', '비밀번호 찾기 기능')}>
              <Text style={styles.linkText}>비밀번호 찾기</Text>
            </TouchableOpacity>
          </View>
          
          <Text style={styles.orText}>또는</Text>
          <View style={styles.socialContainer}>
            <TouchableOpacity style={styles.socialButton}>
                <Text style={styles.socialButtonText}>Google 로그인</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton}>
                <Text style={styles.socialButtonText}>Kakao 로그인</Text>
            </TouchableOpacity>
          </View>

        </View>
      </SafeAreaView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF' },
  container: { flex: 1, paddingHorizontal: 30, paddingTop: 80, alignItems: 'center' },
  logoText: { fontSize: 36, fontWeight: 'bold', color: '#007AFF', marginBottom: 5 },
  subText: { fontSize: 16, color: '#666666', marginBottom: 50 },
  inputGroup: { width: '100%', marginBottom: 20 },
  input: { height: 50, borderColor: '#E0E0E0', borderWidth: 1, borderRadius: 8, paddingHorizontal: 15, marginBottom: 10, fontSize: 16 },
  loginButton: { backgroundColor: '#007AFF', paddingVertical: 14, borderRadius: 8, width: '100%' },
  loginButtonText: { color: '#FFFFFF', fontSize: 18, fontWeight: 'bold', textAlign: 'center' },
  linkContainer: { flexDirection: 'row', marginTop: 15, marginBottom: 50, alignItems: 'center' },
  linkText: { fontSize: 14, color: '#007AFF' },
  separator: { color: '#E0E0E0', marginHorizontal: 10 },
  orText: { fontSize: 14, color: '#AAAAAA', marginBottom: 15 },
  socialContainer: { flexDirection: 'row', width: '100%', justifyContent: 'space-between' },
  socialButton: { flex: 1, paddingVertical: 12, borderWidth: 1, borderColor: '#E0E0E0', borderRadius: 8, alignItems: 'center', marginHorizontal: 5 },
  socialButtonText: { color: '#333333', fontSize: 16 }
});