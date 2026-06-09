import React from 'react';
import { Paperclip } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: number;
  role: 'user' | 'infera';
  content: string;
  imageUrl?: string;
}

// Helper to process raw text nodes and inject custom INFERA UI elements
function processText(text: string): React.ReactNode {
  let nodes: React.ReactNode[] = [text];

  const applyRegex = (
    regex: RegExp, 
    replacer: (match: RegExpExecArray, key: string) => React.ReactNode
  ) => {
    nodes = nodes.flatMap((node, i) => {
      if (typeof node !== 'string') return [node];
      const result: React.ReactNode[] = [];
      let lastIndex = 0;
      let match;
      regex.lastIndex = 0; // reset
      while ((match = regex.exec(node)) !== null) {
        if (match.index > lastIndex) {
          result.push(node.substring(lastIndex, match.index));
        }
        result.push(replacer(match, `${i}-${match.index}`));
        lastIndex = match.index + match[0].length;
      }
      if (lastIndex < node.length) {
        result.push(node.substring(lastIndex));
      }
      return result;
    });
  };

  // 1. Confidence
  applyRegex(/CONFIDENCE:\s*(\d+)%/ig, (match, key) => {
    const val = parseInt(match[1], 10);
    return (
      <div key={`conf-${key}`} className="my-3 block w-full">
        <div className="flex justify-between text-xs font-bold text-textMuted mb-1">
          <span>CONFIDENCE</span>
          <span className="text-accent">{val}%</span>
        </div>
        <div className="w-full h-2 bg-bgCard rounded-full overflow-hidden">
          <div className="h-full bg-accent transition-all duration-1000 ease-out" style={{ width: `${val}%` }}></div>
        </div>
      </div>
    );
  });

  // 2. Scores xx/100 or x/10
  applyRegex(/(\d+(?:\.\d+)?)\/(100|10)\b/g, (match, key) => {
    const num = parseFloat(match[1]);
    const den = parseInt(match[2], 10);
    const percent = (num / den) * 100;
    let colorClass = 'bg-success/20 text-success border-success/30';
    if (percent < 50) colorClass = 'bg-danger/20 text-danger border-danger/30';
    else if (percent < 75) colorClass = 'bg-warning/20 text-warning border-warning/30';
    return (
      <span key={`score-${key}`} className={`inline-block px-2 py-0.5 rounded text-xs font-bold border mx-1 ${colorClass}`}>
        {match[0]}
      </span>
    );
  });

  // 3. Checkmarks
  applyRegex(/✓\s*([^\n]*)/g, (match, key) => {
    return <span key={`check-${key}`} className="text-success inline-flex items-start"><span className="mr-1">✓</span><span>{match[1]}</span></span>;
  });

  // 4. Crosses
  applyRegex(/✗\s*([^\n]*)/g, (match, key) => {
    return <span key={`cross-${key}`} className="text-danger inline-flex items-start"><span className="mr-1">✗</span><span>{match[1]}</span></span>;
  });

  // 5. [CRITICAL]
  applyRegex(/\[CRITICAL\]\s*([^\n]*)/g, (match, key) => {
    return (
      <div key={`crit-${key}`} className="border-l-4 border-danger bg-danger/10 pl-3 py-2 my-2 rounded-r block w-full text-sm font-medium">
        {match[1]}
      </div>
    );
  });

  return <>{nodes}</>;
}

// Recursively apply text processor to ReactMarkdown children
function processNodes(children: React.ReactNode): React.ReactNode {
  return React.Children.map(children, child => {
    if (typeof child === 'string') {
      return processText(child);
    }
    // Only drill down if it's a valid React element
    if (React.isValidElement(child) && child.props) {
      const props = child.props as any;
      if (props.children) {
        return React.cloneElement(child, props, processNodes(props.children));
      }
    }
    return child;
  });
}

export default function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user';
  
  // Extract attachments from the content
  const attachmentRegex = /<attachment name="([^"]+)">([\s\S]*?)<\/attachment>/g;
  let parsedContent = msg.content;
  const attachments: {name: string}[] = [];
  
  let match;
  while ((match = attachmentRegex.exec(msg.content)) !== null) {
    attachments.push({ name: match[1] });
  }
  
  // Remove attachments from the text to be rendered
  parsedContent = parsedContent.replace(attachmentRegex, '').trim();

  // If text contains ━━━, we wrap it in a dark card
  const isCard = parsedContent.includes('━━━');
  
  // Preprocess ━━━ headers for markdown
  let markdownContent = parsedContent.replace(/━━━\s*(.*?)\s*━━━/g, '### $1');

  // ReactMarkdown components
  const components: any = {
    p: ({node, children, ...props}: any) => <p className="mb-1 last:mb-0" {...props}>{processNodes(children)}</p>,
    li: ({node, children, ...props}: any) => <li className="ml-4 list-disc mb-[0.2rem]" {...props}>{processNodes(children)}</li>,
    h1: ({node, children, ...props}: any) => <h1 className="text-2xl font-bold my-4 text-accent uppercase tracking-wider" {...props}>{processNodes(children)}</h1>,
    h2: ({node, children, ...props}: any) => <h2 className="text-xl font-bold my-3 text-accent uppercase tracking-wider" {...props}>{processNodes(children)}</h2>,
    h3: ({node, children, ...props}: any) => <h3 className="text-sm font-bold my-3 text-accent tracking-widest uppercase" {...props}>{processNodes(children)}</h3>,
    h4: ({node, children, ...props}: any) => <h4 className="text-base font-bold my-2 text-accent" {...props}>{processNodes(children)}</h4>,
    ul: ({node, children, ...props}: any) => <ul className="my-3 space-y-1" {...props}>{processNodes(children)}</ul>,
    ol: ({node, children, ...props}: any) => <ol className="my-3 list-decimal ml-5 space-y-1" {...props}>{processNodes(children)}</ol>,
    strong: ({node, children, ...props}: any) => <strong className="font-bold text-white/90" {...props}>{processNodes(children)}</strong>,
    em: ({node, children, ...props}: any) => <em className="italic opacity-90" {...props}>{processNodes(children)}</em>,
    code: ({node, inline, className, children, ...props}: any) => {
      const match = /language-(\w+)/.exec(className || '')
      return inline ? (
        <code className="bg-[#1e293b] px-1.5 py-0.5 rounded text-[13px] text-accent/90 border border-[#334155]" {...props}>
          {children}
        </code>
      ) : (
        <div className="my-4 rounded-lg overflow-hidden border border-[#334155]">
          {match && <div className="bg-[#0f172a] text-xs px-3 py-1 text-slate-400 border-b border-[#334155] uppercase">{match[1]}</div>}
          <pre className="bg-[#1e293b] p-4 overflow-x-auto text-sm text-slate-200">
            <code className={className} {...props}>
              {children}
            </code>
          </pre>
        </div>
      )
    },
    blockquote: ({node, children, ...props}: any) => (
      <blockquote className="border-l-4 border-accent/50 bg-bgCard/30 pl-4 py-2 my-3 rounded-r italic text-slate-300" {...props}>
        {processNodes(children)}
      </blockquote>
    ),
    table: ({node, children, ...props}: any) => (
      <div className="overflow-x-auto my-4 rounded-lg border border-[#334155]">
        <table className="w-full text-left border-collapse" {...props}>
          {processNodes(children)}
        </table>
      </div>
    ),
    th: ({node, children, ...props}: any) => <th className="bg-[#0f172a] p-3 text-sm font-semibold border-b border-[#334155] text-white" {...props}>{processNodes(children)}</th>,
    td: ({node, children, ...props}: any) => <td className="p-3 border-b border-[#334155] text-sm text-slate-300" {...props}>{processNodes(children)}</td>,
    a: ({node, children, href, ...props}: any) => <a href={href} target="_blank" rel="noreferrer" className="text-accent hover:underline decoration-accent/50 underline-offset-2" {...props}>{processNodes(children)}</a>,
  };

  const renderedContent = (
    <ReactMarkdown 
      remarkPlugins={[remarkGfm]} 
      components={components}
    >
      {markdownContent}
    </ReactMarkdown>
  );

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div 
        className={`max-w-[85%] p-4 rounded-lg shadow-sm ${
          isUser ? 'bg-accent text-white rounded-br-none' : 'bg-bgSurface text-textMain rounded-bl-none border border-borderC'
        }`}
      >
        <div className="text-xs text-textMuted mb-2 font-mono tracking-wider flex items-center">
          {isUser ? 'Ishara' : <>Infera</>}
        </div>
        
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {attachments.map((att, i) => (
              <div key={i} className="bg-bgSurface border border-borderC rounded flex items-center px-2 py-1 text-xs text-textMain shadow-sm">
                <Paperclip className="w-3 h-3 mr-1 text-accent" />
                <span className="truncate max-w-[200px] opacity-80">{att.name}</span>
              </div>
            ))}
          </div>
        )}

        {msg.imageUrl && (
          <div className="mb-3">
            <img src={msg.imageUrl} alt="Attached image" className="max-w-[200px] rounded shadow-sm border border-borderC" />
          </div>
        )}

        <div className="whitespace-pre-wrap leading-relaxed text-[15px] prose prose-invert max-w-none">
          {isUser ? (
            parsedContent
          ) : (
            isCard ? (
              <div className="bg-[#0f172a] border border-[#334155] p-6 rounded-xl shadow-lg mt-2">
                {renderedContent}
              </div>
            ) : (
              renderedContent
            )
          )}
        </div>
      </div>
    </div>
  );
}
