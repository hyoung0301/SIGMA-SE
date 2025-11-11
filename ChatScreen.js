import React, { useState, useCallback } from 'react';
import { 
  View, Text, StyleSheet, SafeAreaView, TouchableOpacity, TextInput, FlatList, 
  KeyboardAvoidingView, Platform 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const initialMessages = [
  { id: '1', text: '안녕하세요! SIGMA입니다. 무엇을 도와드릴까요?', type: 'ai' },
  { id: '2', text: '이번 주 중간고사 일정 알려줘', type: 'user' },
  { id: '3', text: `이번 주 중간고사 일정을 확인해드리겠습니다.\n\n• 10월 17일(목) - 소프트웨어공학 (10:00-12:00)\n• 10월 18일(금) - 데이터베이스 (14:00-16:00)\n\n더 궁금한 사항이 있으신가요?`, type: 'ai' },
];

const MessageBubble = ({ message }) => {
  const isUser = message.type === 'user';
  return (
    <View style={[ styles.messageContainer, isUser ? styles.userContainer : styles.aiContainer ]}>
      <Text style={isUser ? styles.userText : styles.aiText}>
        {message.text}
      </Text>
    </View>
  );
};

// ✅ Render Error 해결을 위한 필수 요소: export default function
export default function ChatScreen({ navigation }) {
  const [messages, setMessages] = useState(initialMessages);
  const [inputText, setInputText] = useState('');

  const handleSend = useCallback(() => {
    if (inputText.trim() === '') return;

    const newMessage = {
      id: Date.now().toString(),
      text: inputText.trim(),
      type: 'user',
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInputText('');
  }, [inputText]);

  const renderItem = ({ item }) => <MessageBubble message={item} />;

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        
        {/* 커스텀 헤더 */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Ionicons name="arrow-back-outline" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>SIGMA</Text>
          <Text style={styles.headerSubTitle}>온라인</Text>
          <View style={styles.placeholder} />
        </View>

        {/* 메시지 목록 (FlatList) */}
        <FlatList
          data={messages}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messageList}
        />

        {/* 메시지 입력 영역 */}
        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="메시지를 입력하세요..."
            placeholderTextColor="#AAAAAA"
          />
          <TouchableOpacity 
            style={[styles.sendButton, { backgroundColor: inputText.trim() ? '#007AFF' : '#CCCCCC' }]}
            onPress={handleSend}
            disabled={!inputText.trim()}
          >
            <Ionicons name="send" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// --- 스타일 시트 (이전과 동일) ---
const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF', },
  keyboardAvoidingView: { flex: 1, },
  header: { backgroundColor: '#007AFF', flexDirection: 'row', alignItems: 'center', paddingTop: 10, paddingBottom: 15, paddingHorizontal: 15, },
  backButton: { paddingRight: 15, },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#FFFFFF', },
  headerSubTitle: { fontSize: 14, color: '#DDDDFF', marginLeft: 10, alignSelf: 'flex-end', marginBottom: 2, },
  placeholder: { flex: 1, },
  messageList: { paddingHorizontal: 10, paddingVertical: 10, },
  messageContainer: { maxWidth: '80%', padding: 10, borderRadius: 15, marginVertical: 5, },
  aiContainer: { alignSelf: 'flex-start', backgroundColor: '#F3F4F6', borderTopLeftRadius: 5, marginRight: '20%', },
  aiText: { fontSize: 16, color: '#000000', lineHeight: 22, },
  userContainer: { alignSelf: 'flex-end', backgroundColor: '#007AFF', borderTopRightRadius: 5, marginLeft: '20%', },
  userText: { fontSize: 16, color: '#FFFFFF', lineHeight: 22, },
  inputArea: { flexDirection: 'row', alignItems: 'center', borderTopWidth: 1, borderColor: '#EFEFEF', paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#FFFFFF', },
  textInput: { flex: 1, backgroundColor: '#F3F4F6', borderRadius: 20, paddingHorizontal: 15, paddingVertical: Platform.OS === 'ios' ? 12 : 8, marginRight: 10, fontSize: 16, },
  sendButton: { width: 45, height: 45, borderRadius: 22.5, alignItems: 'center', justifyContent: 'center', },
});