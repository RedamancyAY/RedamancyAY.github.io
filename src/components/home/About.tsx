'use client';

import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import { useState } from 'react';


interface AboutProps {
    content: string;
    title?: string;
    contentEn?: string;
}


export default function About({ content, title = 'About', contentEn }: AboutProps) {
    const [lang, setLang] = useState<'zh' | 'en'>('zh');

    return (
        <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
        >
            <div className="flex items-center mb-4">
                <h2 className="text-2xl font-serif font-bold text-primary mr-4">{title}</h2>
                {contentEn && (
                    <div className="flex space-x-2">
                        <button
                            className={`px-2 py-1 rounded text-sm font-medium border ${lang === 'zh' ? 'bg-accent text-white' : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300'}`}
                            onClick={() => setLang('zh')}
                        >
                            中文
                        </button>
                        <button
                            className={`px-2 py-1 rounded text-sm font-medium border ${lang === 'en' ? 'bg-accent text-white' : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300'}`}
                            onClick={() => setLang('en')}
                        >
                            English
                        </button>
                    </div>
                )}
            </div>
            <div className="text-neutral-700 dark:text-neutral-600 leading-relaxed [&_a]:inline [&_img]:inline [&_img]:align-middle">
                <ReactMarkdown
                    rehypePlugins={[rehypeRaw]}
                    components={{
                        h1: ({ children }) => <h1 className="text-3xl font-serif font-bold text-primary mt-8 mb-4">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-2xl font-serif font-bold text-primary mt-8 mb-4 border-b border-neutral-200 dark:border-neutral-800 pb-2">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-xl font-semibold text-primary mt-6 mb-3">{children}</h3>,
                        p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1 ml-4">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1 ml-4">{children}</ol>,
                        li: ({ children }) => <li className="mb-1">{children}</li>,
                        a: ({ ...props }) => (
                            <a
                                {...props}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-accent font-medium transition-all duration-200 rounded hover:bg-accent/10 hover:shadow-sm"
                            />
                        ),
                        blockquote: ({ children }) => (
                            <blockquote className="border-l-4 border-accent/50 pl-4 italic my-4 text-neutral-600 dark:text-neutral-500">
                                {children}
                            </blockquote>
                        ),
                        strong: ({ children }) => <strong className="font-semibold text-primary">{children}</strong>,
                        em: ({ children }) => <em className="italic text-neutral-600 dark:text-neutral-500">{children}</em>,
                    }}
                >
                    {lang === 'en' && contentEn ? contentEn : content}
                </ReactMarkdown>
            </div>
        </motion.section>
    );
}
