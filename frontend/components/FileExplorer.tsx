"use client";

import React, { useState, useEffect } from 'react';
import { Folder, FileText, ChevronRight, ChevronDown } from 'lucide-react';
import { useWorkspace } from '../context/WorkspaceContext';
import { config } from '../lib/config';

type FileNode = {
    id: string;
    name: string;
    type: 'file' | 'folder';
    children?: FileNode[];
};

const FileTreeItem = ({ node, depth = 0 }: { node: FileNode; depth?: number }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="select-none">
            <div
                className="flex items-center gap-1 hover:bg-gray-800/50 py-1 px-2 rounded cursor-pointer text-sm text-gray-300 transition-colors"
                style={{ paddingLeft: `${depth * 12 + 8}px` }}
                onClick={() => node.type === 'folder' && setIsOpen(!isOpen)}
            >
                {node.type === 'folder' && (
                    <span className="text-gray-500">
                        {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </span>
                )}
                <span className="text-blue-400">
                    {node.type === 'folder' ? <Folder size={14} /> : <FileText size={14} />}
                </span>
                <span className="truncate">{node.name}</span>
            </div>
            {isOpen && node.children && (
                <div>
                    {node.children.map((child) => (
                        <FileTreeItem key={child.id} node={child} depth={depth + 1} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default function FileExplorer() {
    const { currentWorkspace } = useWorkspace();
    const [files, setFiles] = useState<FileNode[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (!currentWorkspace) {
            setFiles([]);
            return;
        }

        const fetchFiles = async () => {
            setIsLoading(true);
            try {
                const res = await fetch(`${config.apiBaseUrl}/workspaces/${currentWorkspace.id}/files`);
                if (res.ok) {
                    const data = await res.json();
                    setFiles(data);
                } else {
                    setFiles([]);
                }
            } catch (error) {
                console.error('Failed to fetch workspace files:', error);
                setFiles([]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchFiles();
    }, [currentWorkspace]);

    return (
        <div className="flex flex-col h-full">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider flex justify-between items-center bg-gray-900/50">
                <span>Files</span>
                <button
                    className="text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Upload File"
                    disabled={!currentWorkspace}
                >
                    +
                </button>
            </div>
            <div className="flex-1 overflow-y-auto py-2">
                {!currentWorkspace ? (
                    <p className="text-center text-xs text-gray-600 mt-4 px-2">
                        Select a workspace
                    </p>
                ) : isLoading ? (
                    <p className="text-center text-xs text-gray-600 mt-4">
                        Loading files...
                    </p>
                ) : files.length === 0 ? (
                    <p className="text-center text-xs text-gray-600 mt-4 px-2">
                        No files in workspace
                    </p>
                ) : (
                    files.map((node) => (
                        <FileTreeItem key={node.id} node={node} />
                    ))
                )}
            </div>
        </div>
    );
}
