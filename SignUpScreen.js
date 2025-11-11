import React, { useState } from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, TextInput, 
  TouchableOpacity, ScrollView, Alert 
} from 'react-native';

const BASE_URL = "https://melina-unrequested-stacee.ngrok-free.dev"; 


export default function SignUpScreen({ navigation }) {
  // 기본 상태
  const [name, setName] = useState('');
  const [studentId, setStudentId] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [major, setMajor] = useState('');

  // 조건부 렌더링을 위한 상태
  const [grade, setGrade] = useState(''); // 학년
  const [userType, setUserType] = useState('student'); // 사용자 유형 (기본값: student)
  const [enrollmentStatus, setEnrollmentStatus] = useState('enrolled'); // 재학 상태 (enrolled/leave)

  const handleSignUp = async () => {
    // 1. 공통 필수 유효성 검사
    if (!name || !studentId || !email || !password || !confirmPassword || !major || !userType) {
      Alert.alert('오류', '모든 필수 정보를 입력하거나 선택해 주세요.');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('오류', '비밀번호와 비밀번호 확인이 일치하지 않습니다.');
      return;
    }

    if (password.length < 8) {
      Alert.alert('오류', '비밀번호는 최소 8자 이상이어야 합니다.');
      return;
    }
    
    // 2. 학생일 경우 추가 유효성 검사
    if (userType === 'student') {
        if (!grade || !enrollmentStatus) {
            Alert.alert('오류', '학생은 학년 및 재학/휴학 상태를 선택해야 합니다.');
            return;
        }
        if (isNaN(grade) || parseInt(grade) < 1 || parseInt(grade) > 4) {
            Alert.alert('오류', '학년은 1에서 4 사이의 숫자로 입력해 주세요.');
            return;
        }
    }

    // 3. API 요청 본문 구성
    const requestBody = {
        name: name,
        studentId: studentId,
        email: email,
        password: password,
        major: major,
        phone: phone,
        userType: userType,
        
        // 조건부 데이터
        grade: userType === 'student' ? parseInt(grade) : null, 
        enrollmentStatus: userType === 'student' ? enrollmentStatus : null,
    };


    try {
      // 4. API 요청 (POST /auth/signup)
      const response = await fetch(`${BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      // 5. 응답 처리 (오류 처리 보강 버전)
      if (response.ok) {
        // 성공 (HTTP 200-299)
        Alert.alert(
          '🎉 회원가입 성공!', 
          '회원가입이 완료되었습니다. 이제 로그인해 주세요.'
        );
        navigation.navigate('Login'); 
      } else {
        // 서버 측 오류 (HTTP 4xx, 5xx)
        let message = `회원가입 실패 (HTTP 상태 코드: ${response.status}).`;
        let serverResponseText = '';

        try {
            serverResponseText = await response.text();
            const errorData = JSON.parse(serverResponseText); 
            message = errorData.message || errorData.error || message;
        } catch (e) {
            if (serverResponseText.length > 0 && serverResponseText.length < 50) {
                 message += ` 서버 응답 본문: ${serverResponseText}`;
            } else {
                 message += ` 서버가 예상치 않은 응답을 보냈습니다.`;
            }
            console.error('JSON 파싱 실패:', e, '서버 텍스트:', serverResponseText);
        }
        
        Alert.alert('회원가입 실패', message);
      }
    } catch (error) {
      // 네트워크 오류 (서버 연결 불가)
      console.error('회원가입 통신 오류:', error);
      Alert.alert(
        '네트워크 오류', 
        '서버에 연결할 수 없습니다. ngrok과 백엔드 서버가 실행 중인지 확인해 주세요.'
      );
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.container}>
          
          <Text style={styles.headline}>새로운 계정을 연결해보세요</Text>

          <View style={styles.inputGroup}>
            <TextInput style={styles.input} placeholder="이름" value={name} onChangeText={setName} />
            <TextInput style={styles.input} placeholder="학번 (예: 20231234)" keyboardType="numeric" value={studentId} onChangeText={setStudentId} />
            <TextInput style={styles.input} placeholder="이메일 (student@university.ac.kr)" keyboardType="email-address" value={email} onChangeText={setEmail} />
            <TextInput style={styles.input} placeholder="전화번호" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
            
            <View style={styles.passwordHint}>
              <TextInput style={styles.input} placeholder="비밀번호 (8자 이상)" secureTextEntry value={password} onChangeText={setPassword} />
              <Text style={styles.hintText}>8자 이상 입력하세요</Text>
            </View>
            
            <TextInput style={styles.input} placeholder="비밀번호 확인" secureTextEntry value={confirmPassword} onChangeText={setConfirmPassword} />
            
            <TextInput style={styles.input} placeholder="학과 (예: 컴퓨터공학과)" value={major} onChangeText={setMajor} />

            {/* 사용자 유형 선택 필드 */}
            <View style={styles.userTypeContainer}>
                <Text style={styles.userTypeLabel}>사용자 유형 선택:</Text>
                <View style={styles.userTypeButtons}>
                    <TouchableOpacity
                        style={[
                            styles.userTypeButton,
                            userType === 'student' && styles.userTypeButtonActive
                        ]}
                        onPress={() => setUserType('student')}
                    >
                        <Text style={[
                            styles.userTypeButtonText,
                            userType === 'student' && styles.userTypeButtonTextActive
                        ]}>학생</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[
                            styles.userTypeButton,
                            userType === 'professor' && styles.userTypeButtonActive
                        ]}
                        onPress={() => setUserType('professor')}
                    >
                        <Text style={[
                            styles.userTypeButtonText,
                            userType === 'professor' && styles.userTypeButtonTextActive
                        ]}>교수</Text>
                    </TouchableOpacity>
                </View>
            </View>
            
            {/* 학생 선택 시에만 렌더링되는 필드 그룹 */}
            {userType === 'student' && (
                <>
                    {/* 학년 입력 필드 */}
                    <TextInput 
                        style={styles.input} 
                        placeholder="학년 (1~4학년)" 
                        keyboardType="numeric" 
                        maxLength={1}
                        value={grade} 
                        onChangeText={setGrade} 
                    />

                    {/* 재학/휴학 선택 필드 */}
                    <View style={styles.enrollmentContainer}>
                        <Text style={styles.userTypeLabel}>재학/휴학 상태:</Text>
                        <View style={styles.userTypeButtons}>
                            <TouchableOpacity
                                style={[
                                    styles.userTypeButton,
                                    enrollmentStatus === 'enrolled' && styles.userTypeButtonActive
                                ]}
                                onPress={() => setEnrollmentStatus('enrolled')}
                            >
                                <Text style={[
                                    styles.userTypeButtonText,
                                    enrollmentStatus === 'enrolled' && styles.userTypeButtonTextActive
                                ]}>재학</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                                style={[
                                    styles.userTypeButton,
                                    enrollmentStatus === 'leave' && styles.userTypeButtonActive
                                ]}
                                onPress={() => setEnrollmentStatus('leave')}
                            >
                                <Text style={[
                                    styles.userTypeButtonText,
                                    enrollmentStatus === 'leave' && styles.userTypeButtonTextActive
                                ]}>휴학</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </>
            )}
          </View>

          {/* 회원가입 버튼 */}
          <TouchableOpacity style={styles.signUpButton} onPress={handleSignUp}>
            <Text style={styles.signUpButtonText}>회원가입</Text>
          </TouchableOpacity>

        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF' },
  scrollContent: { flexGrow: 1, },
  container: { paddingHorizontal: 30, paddingBottom: 30, },
  headline: { fontSize: 20, fontWeight: 'bold', color: '#333333', marginTop: 10, marginBottom: 30, },
  inputGroup: { marginBottom: 30, },
  input: { height: 50, borderColor: '#E0E0E0', borderWidth: 1, borderRadius: 8, paddingHorizontal: 15, marginBottom: 10, fontSize: 16, },
  passwordHint: { marginBottom: 10, },
  hintText: { fontSize: 12, color: '#6A7DFF', marginTop: -8, marginBottom: 10, marginLeft: 5, },
  signUpButton: { backgroundColor: '#007AFF', paddingVertical: 14, borderRadius: 8, },
  signUpButtonText: { color: '#FFFFFF', fontSize: 18, fontWeight: 'bold', textAlign: 'center', },
  
  // 조건부 필드 관련 스타일
  userTypeContainer: { marginBottom: 10, },
  enrollmentContainer: { marginBottom: 10, }, 
  userTypeLabel: { fontSize: 14, color: '#333333', marginBottom: 5, fontWeight: 'bold' },
  userTypeButtons: { flexDirection: 'row', justifyContent: 'space-between' },
  userTypeButton: {
      flex: 1,
      paddingVertical: 12,
      borderWidth: 1,
      borderColor: '#E0E0E0',
      borderRadius: 8,
      alignItems: 'center',
      marginRight: 5, 
      marginLeft: 5, 
      backgroundColor: '#F9F9F9',
  },
  userTypeButtonActive: {
      borderColor: '#007AFF',
      backgroundColor: '#E6F0FF',
  },
  userTypeButtonText: {
      fontSize: 16,
      color: '#333333',
      fontWeight: 'normal',
  },
  userTypeButtonTextActive: {
      color: '#007AFF',
      fontWeight: 'bold',
  },
});