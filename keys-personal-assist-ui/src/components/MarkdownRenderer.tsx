import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';
import { visit } from 'unist-util-visit';
import type { Plugin } from 'unified';
import type { Text, Parent } from 'mdast';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Box, Typography, Link } from '@mui/material';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const remarkAutoLink: Plugin = () => {
  return (tree) => {
    visit(tree, 'text', (node: Text, index, parent) => {
      if (!parent || (parent as Parent).type === 'link') return;

      const urlRegex = /(https?:\/\/[^\s<>")\]]+|www\.[^\s<>")\]]+)/g;
      const matches = Array.from(node.value.matchAll(urlRegex));

      if (matches.length === 0) return;

      const children: (Text | { type: 'link'; url: string; children: Text[] })[] = [];
      let lastIndex = 0;

      matches.forEach((match) => {
        const url = match[0].replace(/[.,;:!?)\]]+$/, '');
        const startIndex = match.index!;

        if (startIndex > lastIndex) {
          children.push({
            type: 'text',
            value: node.value.slice(lastIndex, startIndex),
          });
        }

        children.push({
          type: 'link',
          url: url.startsWith('www.') ? `https://${url}` : url,
          children: [{ type: 'text', value: url }],
        });

        lastIndex = startIndex + match[0].length;
      });

      if (lastIndex < node.value.length) {
        children.push({
          type: 'text',
          value: node.value.slice(lastIndex),
        });
      }

      if (children.length > 0 && parent) {
        (parent as Parent).children.splice(index, 1, ...children as any);
      }
    });
  };
};

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <Box className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkBreaks, remarkGfm, remarkAutoLink]}
        components={{
          p: ({ children }) => (
            <Typography variant="body2" sx={{ mb: 1, lineHeight: 1.6 }}>
              {children}
            </Typography>
          ),
          h1: ({ children }) => (
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, mt: 3 }}>
              {children}
            </Typography>
          ),
          h2: ({ children }) => (
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5, mt: 2 }}>
              {children}
            </Typography>
          ),
          h3: ({ children }) => (
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, mt: 1.5 }}>
              {children}
            </Typography>
          ),
          ul: ({ children }) => (
            <Box component="ul" sx={{ pl: 3, mb: 1, '& li': { mb: 0.5 } }}>
              {children}
            </Box>
          ),
          ol: ({ children }) => (
            <Box component="ol" sx={{ pl: 3, mb: 1, '& li': { mb: 0.5 } }}>
              {children}
            </Box>
          ),
          li: ({ children }) => <li>{children}</li>,
          blockquote: ({ children }) => (
            <Box
              component="blockquote"
              sx={{
                borderLeft: 4,
                borderColor: 'primary.main',
                pl: 2,
                fontStyle: 'italic',
                my: 1,
                color: 'text.secondary',
              }}
            >
              {children}
            </Box>
          ),
          a: ({ href, children }) => (
            <Link href={href} target="_blank" rel="noopener noreferrer" sx={{ color: 'primary.main', cursor: 'pointer' }}>
              {children}
            </Link>
          ),
          code: (props: any) => {
            const { inline, className: codeClassName, children } = props;
            const match = /language-(\w+)/.exec(codeClassName || '');
            const language = match ? match[1] : 'text';

            if (inline) {
              return (
                <Box
                  component="code"
                  sx={{
                    bgcolor: 'action.hover',
                    px: 0.75,
                    py: 0.25,
                    borderRadius: 0.5,
                    fontSize: '0.875rem',
                    fontFamily: 'monospace',
                    color: 'primary.main',
                  }}
                >
                  {children}
                </Box>
              );
            }
            return (
              <SyntaxHighlighter style={oneDark} language={language}>
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
}
