import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '../styles/DocsPage.css';

const DocsPage = () => {
  const [markdownContent, setMarkdownContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReadme = async () => {
      try {
        const response = await fetch('/README.md');
        const text = await response.text();
        setMarkdownContent(text);
      } catch (error) {
        console.error('Ошибка при загрузке README:', error);
        setMarkdownContent('# Ошибка загрузки\n\nНе удалось загрузить документацию.');
      } finally {
        setLoading(false);
      }
    };

    fetchReadme();
  }, []);

  if (loading) {
    return (
      <div className="docs-page">
        <div className="docs-loading">
          <div className="loading-spinner"></div>
          <p>Загрузка документации...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="docs-page">
      <nav className="docs-nav">
        <button onClick={() => window.history.back()} className="back-button">
          ← Назад к игре
        </button>
        <div className="docs-nav-title">Документация</div>
      </nav>
      
      <div className="docs-container">
        <div className="docs-content">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({children}) => <h1 className="docs-h1">{children}</h1>,
              h2: ({children}) => <h2 className="docs-h2">{children}</h2>,
              h3: ({children}) => <h3 className="docs-h3">{children}</h3>,
              h4: ({children}) => <h4 className="docs-h4">{children}</h4>,
              table: ({children}) => <div className="table-container"><table className="docs-table">{children}</table></div>,
              blockquote: ({children}) => <blockquote className="docs-blockquote">{children}</blockquote>,
              code: ({children, ...props}: any) => {
                const isInline = !String(children).includes('\n');
                return isInline 
                  ? <code className="docs-inline-code" {...props}>{children}</code> 
                  : <pre className="docs-code-block"><code {...props}>{children}</code></pre>;
              },
              ul: ({children}) => <ul className="docs-list">{children}</ul>,
              ol: ({children}) => <ol className="docs-list docs-ordered-list">{children}</ol>,
              li: ({children}) => <li className="docs-list-item">{children}</li>,
              strong: ({children}) => <strong className="docs-strong">{children}</strong>,
              em: ({children}) => <em className="docs-em">{children}</em>,
              p: ({children}) => <p className="docs-paragraph">{children}</p>,
            }}
          >
            {markdownContent}
          </ReactMarkdown>
        </div>
        
        <div className="docs-toc">
          <h3>Содержание</h3>
          <ul>
            <li><a href="#цель-игры">🎯 Цель игры</a></li>
            <li><a href="#игровой-процесс">🚀 Игровой процесс</a></li>
            <li><a href="#настройки-игры">⚙️ Настройки игры</a></li>
            <li><a href="#核心-ключевые-концепции">核心 Ключевые концепции</a></li>
            <li><a href="#персонажи">🧙 Персонажи</a></li>
            <li><a href="#общие-карты">🃏 Общие карты</a></li>
            <li><a href="#эффекты">✨ Эффекты</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DocsPage; 