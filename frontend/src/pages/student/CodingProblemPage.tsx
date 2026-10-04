import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import {
  Play, Send, ArrowLeft, CheckCircle2, XCircle, AlertTriangle,
  Clock, Cpu, RotateCcw, Sparkles, Terminal, FileCode, Check
} from 'lucide-react';
import { api } from '@/services/api';
import type { CodingQuestionDetail, CodeRunResponse, CodeSubmission } from '@/types';
import { Badge, LoadingSpinner, useToast } from '@/components/shared';

const STARTER_TEMPLATES: Record<string, string> = {
  python: `import sys

def solve():
    # Read input from standard input
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    # Write your solution logic here
    pass

if __name__ == "__main__":
    solve()
`,
  javascript: `const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    // Write your solution logic here
    
});
`,
  cpp: `#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    // Write your solution logic here
    
    return 0;
}
`,
  java: `import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        
        // Write your solution logic here
        
    }
}
`,
};

export default function CodingProblemPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [question, setQuestion] = useState<CodingQuestionDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [language, setLanguage] = useState<string>('python');
  const [code, setCode] = useState<string>(STARTER_TEMPLATES.python);

  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [runResult, setRunResult] = useState<CodeRunResponse | null>(null);
  const [submissionResult, setSubmissionResult] = useState<CodeSubmission | null>(null);
  const [activeOutputTab, setActiveOutputTab] = useState<'tests' | 'console'>('tests');
  const [selectedCaseIndex, setSelectedCaseIndex] = useState(0);

  useEffect(() => {
    if (slug) {
      loadQuestion(slug);
    }
  }, [slug]);

  async function loadQuestion(questionSlug: string) {
    setIsLoading(true);
    try {
      const data = await api.getCodingQuestion(questionSlug);
      setQuestion(data);
      setCode(STARTER_TEMPLATES[language] || STARTER_TEMPLATES.python);
    } catch (err) {
      console.error('Failed to load coding problem:', err);
      toast('error', 'Problem not found');
      navigate('/student/coding');
    } finally {
      setIsLoading(false);
    }
  }

  function handleLanguageChange(newLang: string) {
    setLanguage(newLang);
    setCode(STARTER_TEMPLATES[newLang] || '');
  }

  async function handleRunCode() {
    if (!question) return;
    setIsRunning(true);
    setRunResult(null);
    setSubmissionResult(null);
    setActiveOutputTab('tests');

    try {
      const result = await api.runCode(question.id, code, language);
      setRunResult(result);
      setSelectedCaseIndex(0);
      if (result.verdict === 'ACCEPTED') {
        toast('success', 'Sample test cases passed!');
      } else {
        toast('info', `Result: ${result.verdict}`);
      }
    } catch (err: any) {
      toast('error', err.response?.data?.detail || 'Failed to execute code');
    } finally {
      setIsRunning(false);
    }
  }

  async function handleSubmitCode() {
    if (!question) return;
    setIsSubmitting(true);
    setRunResult(null);
    setSubmissionResult(null);
    setActiveOutputTab('tests');

    try {
      const sub = await api.submitCode(question.id, code, language);
      setSubmissionResult(sub);
      setSelectedCaseIndex(0);
      if (sub.verdict === 'ACCEPTED') {
        toast('success', `Accepted! +${sub.score} marks`);
      } else {
        toast('info', `Submission Verdict: ${sub.verdict}`);
      }
    } catch (err: any) {
      toast('error', err.response?.data?.detail || 'Submission failed');
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading || !question) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const activeResult = submissionResult || runResult;
  const testResultsList = submissionResult ? submissionResult.test_results : runResult?.test_results || [];
  const currentCase = testResultsList[selectedCaseIndex];

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between gap-4">
        <button
          onClick={() => navigate('/student/coding')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-white transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Problems
        </button>

        <div className="flex items-center gap-3">
          <Badge
            variant={
              question.difficulty === 'EASY'
                ? 'success'
                : question.difficulty === 'MEDIUM'
                ? 'warning'
                : 'error'
            }
          >
            {question.difficulty}
          </Badge>
          <span className="text-xs font-semibold text-muted-foreground px-2.5 py-1 rounded-lg bg-white/5 border border-border/40">
            {question.marks} Marks
          </span>
        </div>
      </div>

      {/* Main Workspace: Left Problem Info, Right Monaco Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT PANE: Problem Description */}
        <div className="lg:col-span-5 space-y-5 glass-card p-6 rounded-2xl border border-border/60 max-h-[82vh] overflow-y-auto">
          <div>
            <h1 className="text-2xl font-bold font-display text-white">{question.title}</h1>
            <div className="flex items-center gap-2 mt-1.5 text-xs text-muted-foreground">
              <span>{question.topic_name || 'Programming'}</span>
              <span>•</span>
              <span>Time Limit: {question.time_limit_ms}ms</span>
              <span>•</span>
              <span>Memory Limit: {question.memory_limit_mb}MB</span>
            </div>
          </div>

          <div className="space-y-4 text-xs text-foreground/90 leading-relaxed border-t border-border/40 pt-4">
            <div>
              <h3 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-2">
                Problem Statement
              </h3>
              <p className="whitespace-pre-line leading-relaxed text-muted-foreground">
                {question.problem_statement}
              </p>
            </div>

            {question.input_format && (
              <div>
                <h3 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-1">
                  Input Format
                </h3>
                <p className="whitespace-pre-line text-muted-foreground">{question.input_format}</p>
              </div>
            )}

            {question.output_format && (
              <div>
                <h3 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-1">
                  Output Format
                </h3>
                <p className="whitespace-pre-line text-muted-foreground">{question.output_format}</p>
              </div>
            )}

            {question.examples && question.examples.length > 0 && (
              <div className="space-y-3 pt-2">
                <h3 className="font-semibold text-white uppercase tracking-wider text-[11px]">
                  Sample Examples
                </h3>
                {question.examples.map((ex, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-black/40 border border-border/40 space-y-2">
                    <div className="text-[11px] font-semibold text-forge-400">Example {idx + 1}:</div>
                    <div>
                      <span className="text-muted-foreground text-[10px] uppercase font-bold">Input:</span>
                      <pre className="font-mono text-xs text-slate-200 mt-0.5 bg-white/5 p-2 rounded-lg overflow-x-auto">
                        {ex.input}
                      </pre>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-[10px] uppercase font-bold">Output:</span>
                      <pre className="font-mono text-xs text-slate-200 mt-0.5 bg-white/5 p-2 rounded-lg overflow-x-auto">
                        {ex.output}
                      </pre>
                    </div>
                    {ex.explanation && (
                      <div className="text-muted-foreground text-[11px] italic pt-1">
                        Explanation: {ex.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {question.constraints && (
              <div className="pt-2">
                <h3 className="font-semibold text-white uppercase tracking-wider text-[11px] mb-1">
                  Constraints
                </h3>
                <pre className="font-mono text-[11px] text-muted-foreground bg-white/5 p-2.5 rounded-xl border border-border/30 whitespace-pre-line">
                  {question.constraints}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANE: Monaco Code Editor & Execution Panel */}
        <div className="lg:col-span-7 space-y-4">
          <div className="glass-card rounded-2xl border border-border/60 overflow-hidden shadow-xl">
            {/* Editor Toolbar */}
            <div className="p-3 bg-black/40 border-b border-border/40 flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <FileCode size={16} className="text-forge-400" />
                <span className="text-xs font-semibold text-white">Solution Editor</span>
              </div>

              <div className="flex items-center gap-3">
                <select
                  value={language}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  className="px-3 py-1.5 rounded-xl bg-white/5 border border-border/60 text-xs font-semibold text-foreground focus:outline-none focus:border-forge-500"
                >
                  <option value="python" className="bg-card text-foreground">Python 3</option>
                  <option value="javascript" className="bg-card text-foreground">JavaScript (Node.js)</option>
                  <option value="cpp" className="bg-card text-foreground">C++ (GCC 9.2)</option>
                  <option value="java" className="bg-card text-foreground">Java (OpenJDK 13)</option>
                </select>

                <button
                  onClick={() => setCode(STARTER_TEMPLATES[language] || '')}
                  title="Reset to starter template"
                  className="p-1.5 text-muted-foreground hover:text-white rounded-lg hover:bg-white/5 transition-colors"
                >
                  <RotateCcw size={14} />
                </button>
              </div>
            </div>

            {/* Monaco Editor Container */}
            <div className="h-[430px] border-b border-border/40">
              <Editor
                height="100%"
                language={language === 'cpp' ? 'cpp' : language === 'javascript' ? 'javascript' : language === 'java' ? 'java' : 'python'}
                value={code}
                onChange={(val) => setCode(val || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  fontFamily: 'JetBrains Mono, Menlo, monospace',
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  padding: { top: 12, bottom: 12 },
                }}
              />
            </div>

            {/* Run / Submit Action Bar */}
            <div className="p-3 bg-black/30 flex items-center justify-between gap-4">
              <div className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                <Cpu size={14} className="text-forge-400" />
                Judge0 Isolated Sandboxed Runtime
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleRunCode}
                  disabled={isRunning || isSubmitting}
                  className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold text-xs transition-all flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isRunning ? <LoadingSpinner size="sm" /> : <Play size={14} />}
                  Run Code
                </button>

                <button
                  onClick={handleSubmitCode}
                  disabled={isRunning || isSubmitting}
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-forge-500 to-purple-600 hover:from-forge-400 hover:to-purple-500 text-white font-semibold text-xs transition-all flex items-center gap-1.5 glow-button shadow-lg shadow-forge-500/20 disabled:opacity-50"
                >
                  {isSubmitting ? <LoadingSpinner size="sm" /> : <Send size={14} />}
                  Submit Solution
                </button>
              </div>
            </div>
          </div>

          {/* Test Case Execution Output Panel */}
          {activeResult && (() => {
            const passedCount = submissionResult ? submissionResult.test_cases_passed : runResult?.passed_tests || 0;
            const totalCount = submissionResult ? submissionResult.test_cases_total : runResult?.total_tests || 0;
            const timeMs = submissionResult ? (submissionResult.runtime_ms || 0) : (runResult?.execution_time_ms || 0);
            const memKb = submissionResult ? (submissionResult.memory_kb || 0) : (runResult?.memory_kb || 0);
            const compileOut = submissionResult ? submissionResult.compile_output : runResult?.compile_output;
            const errOut = submissionResult ? null : runResult?.stderr;

            return (
              <div className="glass-card rounded-2xl border border-border/60 overflow-hidden shadow-lg animate-fade-in">
                <div className="p-3 bg-black/40 border-b border-border/40 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2.5 py-1 rounded-lg text-xs font-bold font-display uppercase tracking-wider ${
                        activeResult.verdict === 'ACCEPTED'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : activeResult.verdict === 'WRONG_ANSWER'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {activeResult.verdict.replace(/_/g, ' ')}
                    </span>

                    <span className="text-xs text-muted-foreground">
                      Passed: <strong>{passedCount} / {totalCount}</strong> test cases
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock size={12} /> {timeMs} ms
                    </span>
                    <span className="flex items-center gap-1">
                      <Cpu size={12} /> {memKb} KB
                    </span>
                  </div>
                </div>

                {/* Sub-Tabs: Test Cases vs Compiler Output */}
                <div className="p-4 space-y-3">
                  <div className="flex items-center gap-2 border-b border-border/30 pb-2">
                    {testResultsList.map((tc, idx) => (
                      <button
                        key={tc.test_case_id}
                        onClick={() => setSelectedCaseIndex(idx)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                          selectedCaseIndex === idx
                            ? 'bg-white/10 text-white border border-white/20'
                            : 'text-muted-foreground hover:bg-white/5'
                        }`}
                      >
                        {tc.passed ? (
                          <CheckCircle2 size={13} className="text-emerald-400" />
                        ) : (
                          <XCircle size={13} className="text-red-400" />
                        )}
                        <span>Case {idx + 1} {tc.is_sample ? '(Sample)' : '(Hidden)'}</span>
                      </button>
                    ))}

                    {(compileOut || errOut) && (
                      <button
                        onClick={() => setActiveOutputTab('console')}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold text-amber-400 hover:bg-amber-500/10 flex items-center gap-1.5 transition-colors ml-auto"
                      >
                        <Terminal size={13} />
                        Compiler Logs
                      </button>
                    )}
                  </div>

                  {/* Display Current Selected Case Result */}
                  {currentCase && activeOutputTab === 'tests' && (
                    <div className="space-y-3 pt-1 text-xs">
                      {currentCase.is_sample ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div>
                            <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">
                              Input:
                            </div>
                            <pre className="font-mono bg-black/40 p-2.5 rounded-xl border border-border/40 text-foreground overflow-x-auto">
                              {currentCase.input}
                            </pre>
                          </div>
                          <div>
                            <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">
                              Expected Output:
                            </div>
                            <pre className="font-mono bg-black/40 p-2.5 rounded-xl border border-border/40 text-emerald-300 overflow-x-auto">
                              {currentCase.expected_output}
                            </pre>
                          </div>
                          <div className="sm:col-span-2">
                            <div className="text-[10px] uppercase font-bold text-muted-foreground mb-1">
                              Your Output:
                            </div>
                            <pre className="font-mono bg-black/40 p-2.5 rounded-xl border border-border/40 text-foreground overflow-x-auto">
                              {currentCase.stdout || '(no output)'}
                            </pre>
                          </div>
                        </div>
                      ) : (
                        <div className="p-4 rounded-xl bg-white/5 border border-border/40 text-center">
                          <div className="font-semibold text-xs text-foreground mb-1">
                            Hidden Test Case
                          </div>
                          <p className="text-[11px] text-muted-foreground">
                            Test inputs and expected outputs are hidden to maintain assessment integrity.
                            Status: <strong>{currentCase.status}</strong> ({currentCase.runtime_ms}ms)
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Compiler / Error Console */}
                  {activeOutputTab === 'console' && (
                    <div className="p-3 bg-red-950/20 border border-red-500/30 rounded-xl space-y-1">
                      <div className="text-[11px] font-bold text-red-400">Compilation / Runtime Traceback:</div>
                      <pre className="font-mono text-xs text-red-200 whitespace-pre-wrap">
                        {compileOut || errOut || 'No compile errors.'}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}
