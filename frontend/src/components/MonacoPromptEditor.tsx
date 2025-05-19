import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface MonacoPromptEditorProps {
  value?: string;
  onChange?: (value: string | undefined) => void;
  height?: string;
  suggestions?: Array<{
    label: string;
    detail?: string;
  }>;
  editorId?: string;
}

const MonacoPromptEditor: React.FC<MonacoPromptEditorProps> = ({
  value = '',
  onChange,
  height = '200px',
  suggestions = [],
  editorId = 'default'
}) => {
  // 使用useRef确保只注册一次提供器
  const providerRef = useRef<any>(null);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  // console.log(suggestions);
  // 注册自动完成提供器
  const registerCompletionProvider = (monaco: any) => {
    // 如果已经注册过提供器，先移除它
    if (providerRef.current) {
      providerRef.current.dispose();
      providerRef.current = null;
    }
    
    // 使用唯一的语言ID
    const uniqueLanguageId = `markdown-${editorId}`;
    
    // 注册自定义语言
    if (!monaco.languages.getLanguages().some((lang: any) => lang.id === uniqueLanguageId)) {
      monaco.languages.register({ 
        id: uniqueLanguageId,
        extensions: ['.md'],
        aliases: ['Markdown', uniqueLanguageId],
        mimetypes: ['text/markdown']
      });
    }
    
    // 注册新的提供器
    providerRef.current = monaco.languages.registerCompletionItemProvider(uniqueLanguageId, {
      triggerCharacters: ['{', '@'],
      provideCompletionItems: (model: any, position: any) => {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: position.lineNumber,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        });
        
        const hasOpenBrace = textUntilPosition.endsWith('{');
        const word = model.getWordUntilPosition(position);
        
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: hasOpenBrace ? position.column : word.startColumn,
          endColumn: position.column
        };

        return {
          suggestions: suggestions.map((item, index) => {
            let insertText = item.label;
            if (hasOpenBrace && insertText.startsWith('{')) {
              insertText = insertText.substring(1);
            }
            
            if (insertText.endsWith('}') && hasOpenBrace) {
              insertText = insertText.substring(0, insertText.length - 1);
            }

            // 如果是左括号触发的补全，确保添加右括号
            if (hasOpenBrace && !insertText.endsWith('}')) {
              insertText = `${insertText}}`; // 添加右括号
            }
            
            return {
              label: item.label,
              kind: monaco.languages.CompletionItemKind.Text,
              insertText: insertText,
              detail: item.detail || '',
              range: range,
              sortText: `${index}`.padStart(5, '0'),
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
            };
          })
        };
      }
    });
  };
  
  // 编辑器挂载时的处理
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // 注册自动完成提供器
    registerCompletionProvider(monaco);
    
    // 配置编辑器选项
    editor.updateOptions({
      fontSize: 14,
      lineHeight: 20,
      quickSuggestions: {
        other: true,
        comments: true,
        strings: true
      },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnEnter: 'on',
      tabCompletion: 'on',
      wordBasedSuggestions: 'on',
      autoClosingBrackets: 'always',  // 添加自动闭合括号的配置
      autoClosingQuotes: 'always',    // 添加自动闭合引号的配置
      suggest: {
        showIcons: true,
        insertMode: 'insert',
        filterGraceful: true,
        snippetsPreventQuickSuggestions: false,
        localityBonus: true,
        shareSuggestSelections: true,
        showMethods: true,
        showFunctions: true,
        showVariables: true,
        showClasses: true,
        showWords: true,
        preview: true,
        previewMode: 'prefix',
        showInlineDetails: true
      }
    });
  };
  
  // 当suggestions变化时重新注册提供器
  useEffect(() => {
    if (monacoRef.current) {
      registerCompletionProvider(monacoRef.current);
    }
  }, [suggestions]);
  
  // 组件卸载时清理
  useEffect(() => {
    return () => {
      if (providerRef.current) {
        providerRef.current.dispose();
      }
    };
  }, []);

  return (
    <Editor
      height={height}
      defaultLanguage={`markdown-${editorId}`}
      theme="vs-light"
      value={value}
      onChange={onChange}
      onMount={handleEditorDidMount}
      options={{
        minimap: { enabled: false },
        lineNumbers: 'off',
        folding: false,
        wordWrap: 'on',
        contextmenu: false,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        fontSize: 16,
        fontFamily: "'Menlo', 'Monaco', 'Courier New', monospace",
        lineHeight: 22,
        padding: { top: 10, bottom: 10 },
        renderLineHighlight: 'none',
        overviewRulerLanes: 0,
        hideCursorInOverviewRuler: true,
        overviewRulerBorder: false,
        quickSuggestions: true,
        suggestOnTriggerCharacters: true,
        acceptSuggestionOnEnter: 'on',
        tabCompletion: 'on',
        links: true,
        formatOnType: true
      }}
    />
  );
};

export default MonacoPromptEditor; 