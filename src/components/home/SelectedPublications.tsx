'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Publication } from '@/types/publication';
import { cn } from '@/lib/utils';

interface SelectedPublicationsProps {
    publications: Publication[];
    title?: string;
    enableOnePageMode?: boolean;
}

export default function SelectedPublications({ publications, title = 'Selected Publications', enableOnePageMode = false }: SelectedPublicationsProps) {
    return (
        <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
        >
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-serif font-bold text-primary">{title}</h2>
                <Link
                    href={enableOnePageMode ? "/#publications" : "/publications"}
                    prefetch={true}
                    className="text-accent hover:text-accent-dark text-sm font-medium transition-all duration-200 rounded hover:bg-accent/10 hover:shadow-sm"
                >
                    View All →
                </Link>
            </div>
            <div className="space-y-4">
                {publications.map((pub, index) => (
                    <motion.div
                        key={pub.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, delay: 0.1 * index }}
                        className={cn(
                            "p-4 rounded-lg shadow-sm border transition-all duration-200 hover:shadow-lg hover:scale-[1.02]",
                            pub.ccf === 'A' ? "bg-red-50/50 dark:bg-red-900/10 border-red-100 dark:border-red-900/20" :
                                pub.ccf === 'B' ? "bg-yellow-50/50 dark:bg-yellow-900/10 border-yellow-100 dark:border-yellow-900/20" :
                                    pub.ccf === 'C' ? "bg-green-50/50 dark:bg-green-900/10 border-green-100 dark:border-green-900/20" :
                                        "bg-neutral-50 dark:bg-neutral-800 border-neutral-200 dark:border-[rgba(148,163,184,0.24)]",
                            "relative" // Add relative positioning
                        )}
                    >
                        {/* Type Badge */}
                        <div className={cn(
                            "absolute top-0 right-0 px-3 py-1 text-xs font-semibold rounded-bl-lg rounded-tr-lg",
                            pub.type === 'journal' ? "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300" :
                                pub.type === 'conference' ? "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300" :
                                    "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                        )}>
                            {pub.type === 'journal' ? 'Journal' :
                                pub.type === 'conference' ? 'Conference' :
                                    pub.type.replace('-', ' ')}
                        </div>
                        <h3 className="font-semibold text-primary mb-2 leading-tight">
                            {pub.title}
                        </h3>
                        <p className="text-sm text-neutral-600 dark:text-neutral-500 mb-1">
                            {pub.authors.map((author, idx) => (
                                <span key={idx}>
                                    <span className={`${author.isHighlighted ? 'font-semibold text-accent' : ''} ${author.isCoAuthor ? `underline underline-offset-4 ${author.isHighlighted ? 'decoration-accent' : 'decoration-neutral-400'}` : ''}`}>
                                        {author.name}
                                    </span>
                                    {author.isCorresponding && (
                                        <sup className={`ml-0 ${author.isHighlighted ? 'text-accent' : 'text-neutral-600 dark:text-neutral-500'}`}>†</sup>
                                    )}
                                    {idx < pub.authors.length - 1 && ', '}
                                </span>
                            ))}
                        </p>
                        <p className="text-sm text-neutral-600 dark:text-neutral-500 mb-2">
                            {pub.journal || pub.conference}
                            {pub.ccf && (
                                <span className={cn(
                                    "ml-2 px-2 py-0.5 text-xs font-medium rounded",
                                    pub.ccf === 'A' ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                                        pub.ccf === 'B' ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
                                            "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                                )}>
                                    CCF-{pub.ccf}
                                </span>
                            )}
                            {pub.quartile && (
                                <span className={cn(
                                    "ml-2 px-2 py-0.5 text-xs font-medium rounded",
                                    pub.quartile === 'Q1' ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                                        pub.quartile === 'Q2' ? "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400" :
                                            "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                )}>
                                    JCR-{pub.quartile}
                                </span>
                            )}
                            {pub.cas && (
                                <span className={cn(
                                    "ml-2 px-2 py-0.5 text-xs font-medium rounded",
                                    pub.cas === '1区' ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                                        pub.cas === '2区' ? "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400" :
                                            "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                )}>
                                    CAS-{pub.cas}
                                </span>
                            )}
                            {pub.impactFactor && (
                                <span className="ml-2 px-2 py-0.5 text-xs font-medium rounded bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                                    IF: {pub.impactFactor}
                                </span>
                            )}
                        </p>
                        {pub.description && (
                            <p className="text-sm text-neutral-500 dark:text-neutral-500 line-clamp-2">
                                {pub.description}
                            </p>
                        )}
                    </motion.div>
                ))}
            </div>
        </motion.section>
    );
}
