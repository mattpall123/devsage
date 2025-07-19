"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Upload, Folder, File, ChevronRight, ChevronDown } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface FileNode {
  name: string
  path: string
  type: "file" | "folder"
  children?: FileNode[]
  content?: string
}

export default function Home() {
  const [isDragOver, setIsDragOver] = useState(false)
  const [fileTree, setFileTree] = useState<FileNode | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const buildFileTree = (files: FileList): FileNode => {
    const root: FileNode = { name: "root", path: "", type: "folder", children: [] }

    Array.from(files).forEach((file) => {
      const pathParts = file.webkitRelativePath.split("/")
      let currentNode = root

      pathParts.forEach((part, index) => {
        if (!currentNode.children) currentNode.children = []

        let existingNode = currentNode.children.find((child) => child.name === part)

        if (!existingNode) {
          const isFile = index === pathParts.length - 1
          existingNode = {
            name: part,
            path: pathParts.slice(0, index + 1).join("/"),
            type: isFile ? "file" : "folder",
            children: isFile ? undefined : [],
          }

          if (isFile) {
            const reader = new FileReader()
            reader.onload = (e) => {
              existingNode!.content = e.target?.result as string
            }
            reader.readAsText(file)
          }

          currentNode.children.push(existingNode)
        }

        currentNode = existingNode
      })
    })

    return root.children?.[0] || root
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const items = Array.from(e.dataTransfer.items)
    const files: File[] = []

    const processEntry = async (entry: FileSystemEntry, path = "") => {
      if (entry.isFile) {
        const fileEntry = entry as FileSystemFileEntry
        return new Promise<void>((resolve) => {
          fileEntry.file((file) => {
            Object.defineProperty(file, "webkitRelativePath", {
              value: path + file.name,
              writable: false,
            })
            files.push(file)
            resolve()
          })
        })
      } else if (entry.isDirectory) {
        const dirEntry = entry as FileSystemDirectoryEntry
        const reader = dirEntry.createReader()
        return new Promise<void>((resolve) => {
          reader.readEntries(async (entries) => {
            await Promise.all(entries.map((childEntry) => processEntry(childEntry, path + entry.name + "/")))
            resolve()
          })
        })
      }
    }

    Promise.all(
      items.map((item) => {
        const entry = item.webkitGetAsEntry()
        return entry ? processEntry(entry) : Promise.resolve()
      }),
    ).then(() => {
      if (files.length > 0) {
        const fileList = new DataTransfer()
        files.forEach((file) => fileList.items.add(file))
        const tree = buildFileTree(fileList.files)
        setFileTree(tree)
      }
    })
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const tree = buildFileTree(files)
      setFileTree(tree)
    }
  }

  const FileTreeNode = ({ node, level = 0 }: { node: FileNode; level?: number }) => {
    const [isOpen, setIsOpen] = useState(level < 2)

    if (node.type === "file") {
      return (
        <div
          className={`flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-muted ${
            selectedFile === node.path ? "bg-muted" : ""
          }`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
          onClick={() => setSelectedFile(node.path)}
        >
          <File className="h-4 w-4 text-blue-500" />
          <span className="text-sm">{node.name}</span>
        </div>
      )
    }

    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <div
            className="flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-muted"
            style={{ paddingLeft: `${level * 20 + 8}px` }}
          >
            {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            <Folder className="h-4 w-4 text-yellow-500" />
            <span className="text-sm font-medium">{node.name}</span>
          </div>
        </CollapsibleTrigger>
        <CollapsibleContent>
          {node.children?.map((child, index) => (
            <FileTreeNode key={index} node={child} level={level + 1} />
          ))}
        </CollapsibleContent>
      </Collapsible>
    )
  }

  const selectedFileContent = selectedFile && fileTree ? findFileContent(fileTree, selectedFile) : null

  function findFileContent(node: FileNode, path: string): string | null {
    if (node.path === path && node.type === "file") {
      return node.content || ""
    }

    if (node.children) {
      for (const child of node.children) {
        const result = findFileContent(child, path)
        if (result !== null) return result
      }
    }

    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-full mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Project Folder Uploader</h1>
          <p className="text-slate-600 text-lg">Drop your project folder to explore its structure and files</p>
        </div>

        {!fileTree ? (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload Project Folder
              </CardTitle>
              <CardDescription>
                Drag and drop a folder containing your project files, or click to browse
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                  isDragOver ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-slate-400"
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
              >
                <Upload className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-slate-700 mb-2">Drop your project folder here</p>
                <p className="text-slate-500 mb-4">or click to browse and select a folder</p>
                <input
                  type="file"
                  webkitdirectory=""
                  directory=""
                  multiple
                  onChange={handleFileInput}
                  className="hidden"
                  id="folder-input"
                />
                <Button asChild>
                  <label htmlFor="folder-input" className="cursor-pointer">
                    Browse Folder
                  </label>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-6 gap-6">
            {/* Project Structure Card - Furthest Left */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Folder className="h-5 w-5" />
                  Project Structure
                </CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setFileTree(null)}>
                    Upload New
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[600px]">
                  <div className="p-4">{fileTree && <FileTreeNode node={fileTree} />}</div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Documentation Generation Card - Same width as File Preview */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Generate Documentation
                </CardTitle>
                <CardDescription>Create high-level documentation for your project</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button className="w-full" disabled={!fileTree}>
                    Generate Documentation
                  </Button>
                  <div className="pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Upload a project folder to generate comprehensive documentation using AI analysis.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* File Preview Card */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <File className="h-5 w-5" />
                  File Preview
                </CardTitle>
                <CardDescription>
                  {selectedFile ? `Viewing: ${selectedFile}` : "Select a file to preview its content"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[600px] w-full">
                  {selectedFileContent ? (
                    <div className="min-w-max">
                      <pre className="text-sm bg-slate-50 p-4 rounded-lg whitespace-pre overflow-visible">
                        <code className="block">{selectedFileContent}</code>
                      </pre>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-500">
                      <div className="text-center">
                        <File className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Select a file from the project structure to view its content</p>
                      </div>
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
