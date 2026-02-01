"use client"

import ReactMarkdown from "react-markdown"
import remarkBreaks from "remark-breaks"
import remarkGfm from "remark-gfm"
import { visit } from "unist-util-visit"
import type { Plugin } from "unified"
import type { Text } from "mdast"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"
import type { ReactNode } from "react"

interface MarkdownRendererProps {
  content: string
  className?: string
}

const remarkAutoLink: Plugin = () => {
  return (tree) => {
    visit(tree, "text", (node: Text, index, parent) => {
      if (!parent || parent.type === "link") return

      const urlRegex = /(https?:\/\/[^\s<>")\]]+|www\.[^\s<>")\]]+)/g
      const matches = Array.from(node.value.matchAll(urlRegex))

      if (matches.length === 0) return

      const children: (Text | { type: "link"; url: string; children: Text[] })[] = []
      let lastIndex = 0

      matches.forEach((match) => {
        const url = match[0].replace(/[.,;:!?)\]]+$/, "")
        const startIndex = match.index!

        if (startIndex > lastIndex) {
          children.push({
            type: "text",
            value: node.value.slice(lastIndex, startIndex),
          })
        }

        children.push({
          type: "link",
          url: url.startsWith("www.") ? `https://${url}` : url,
          children: [{ type: "text", value: url }],
        })

        lastIndex = startIndex + match[0].length
      })

      if (lastIndex < node.value.length) {
        children.push({
          type: "text",
          value: node.value.slice(lastIndex),
        })
      }

      if (children.length > 0) {
        parent.children.splice(index, 1, ...children)
      }
    })
  }
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkBreaks, remarkGfm, remarkAutoLink]}
        components={{
          p: ({ children }) => <p className="mb-2 leading-relaxed">{children}</p>,
          h1: ({ children }) => <h1 className="text-xl font-bold mb-3 mt-4">{children}</h1>,
          h2: ({ children }) => <h2 className="text-lg font-bold mb-2 mt-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-bold mb-2 mt-2">{children}</h3>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="ml-2">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-emerald-600 pl-4 italic my-2 text-muted-foreground">
              {children}
            </blockquote>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer"
            >
              {children}
            </a>
          ),
          code: ({
            inline,
            className: codeClassName,
            children,
          }: { inline?: boolean; className?: string; children: ReactNode }) => {
            const match = /language-(\w+)/.exec(codeClassName || "")
            const language = match ? match[1] : "text"

            if (inline) {
              return (
                <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-emerald-600 dark:text-emerald-400">
                  {children}
                </code>
              )
            }
            return (
              <SyntaxHighlighter style={oneDark} language={language}>
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
