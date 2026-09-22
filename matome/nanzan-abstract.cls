% nanzan-abstract.cls (Bilingual jlreq-based Class)
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nanzan-abstract}[2026/05/30 Document Class for Nanzan Abstract (Bilingual)]

% ==========================================
% オプションの定義
% ==========================================
% ページ番号を消すフラグの初期化
\newif\if@nopagenumber \@nopagenumberfalse
\DeclareOption{no-page-number}{\@nopagenumbertrue}

% 英語モードのフラグの初期化（デフォルトは偽＝日本語）
\newif\if@english \@englishfalse
\DeclareOption{english}{\@englishtrue}

% その他の未定義オプションはすべてベースクラス（jlreq）に引き渡す
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{jlreq}}
\ProcessOptions\relax

% ==========================================
% 1. ベースクラスの読み込み (jlreq)
% ==========================================
\LoadClass[
  article,
  paper=a4,
  fontsize=10pt,
  twocolumn,
  twoside,
  baselineskip=13pt,
  head_space=21.5mm,
  foot_space=21.5mm,
  gutter=18mm,
  fore_edge=18mm,
  column_gap=4mm
]{jlreq}

% ==========================================
% 2. 外部パッケージの読み込み
% ==========================================
\RequirePackage{jlreq-complements}
\RequirePackage{enumitem}
\RequirePackage{mathtools}
\RequirePackage{amsthm}
\RequirePackage{graphicx}
\RequirePackage{iftex}

% 欧文フォント（タイムズ系）
\RequirePackage[full]{textcomp}               % 記号類の補完
\RequirePackage[defaultsups]{newtxtext}       % 脚注記号は LaTeX 標準のまま
\RequirePackage[bigdelims,vvarbb]{newtxmath}  % 黒板太字は STIX
\RequirePackage[cal=boondoxo]{mathalfa}       % 花文字

\ifluatex
  \RequirePackage{luatexja-fontspec}
  % タイプライタ体
  \setmonofont[StylisticSet={1,3}]{Inconsolatazi4-Regular}
\else
  \ifuptex
    \usepackage[T1]{fontenc}
    % タイプライタ体
    \RequirePackage[varqu,varl]{inconsolata}
  \fi
\fi

% ==========================================
% 3. タイトルまわりの設定（日本語／英語の切り替え）
% ==========================================
\newcommand{\subtitle}[1]{\gdef\@subtitle{#1}} \subtitle{}
\newcommand{\professor}[1]{\gdef\@professor{#1}} \professor{}

\renewcommand{\maketitle}{%
  \twocolumn[{
    \begin{center}
      \vskip 1em
      {\LARGE\bfseries \@title \par}
      \vskip 0.5em
      \ifx\@subtitle\@empty
        {\Large\bfseries \vbox{\phantom{—\quad —}}\par}
      \else
        \if@english
          {\Large\bfseries --- \@subtitle --- \par} % 英語：ダッシュ記号
        \else
          {\Large\bfseries —\@subtitle —\par}      % 日本語：全角ダッシュ
        \fi
      \fi
      \vskip 1.5em
      {\normalsize \@author \par}
      \vskip 0.5em
      \ifx\@professor\@empty
      \else
        \if@english
          {\normalsize Advisor: \@professor \par}    % 英語：Advisor
        \else
          {\normalsize 指導教員：\@professor \par}  % 日本語：指導教員
        \fi
      \fi
      \vskip 1.5em
    \end{center}
  }]
  % ページ番号消去の判定
  \if@nopagenumber
    \thispagestyle{empty}
    \pagestyle{empty}
  \fi
}

% ==========================================
% 4. 見出しの見た目・余白設定 (jlreqスタイル)
% ==========================================
\ModifyHeading{section}{
  font={\large\bfseries},
  format={\vbox{\noindent #1#2}},
  lines=2,
  before_space=1.5ex,
  after_space=1.0ex
}

\ModifyHeading{subsection}{
  font={\normalsize\bfseries},
  format={\vbox{\noindent #1#2}},
  lines=2,
  before_space=1.5ex,
  after_space=1.0ex
}

\ModifyHeading{subsubsection}{
  font={\normalsize\bfseries},
  format={\vbox{\noindent #1#2}},
  lines=2,
  before_space=1.5ex,
  after_space=1.0ex
}

\ModifyHeading{paragraph}{
  font={\normalsize\bfseries},
  label_format={\theparagraph},
  after_label_space=1em,
  after_space=1em
}

% ==========================================
% 5. 箇条書きの行間調整 (enumitem)
% ==========================================
\setlist{
  leftmargin=*, 
  topsep=0pt,    
  parsep=0pt,    
  itemsep=0pt,   
  partopsep=0pt  
}

% ==========================================
% 6. 日本語／英語の違い吸収
% ==========================================
\theoremstyle{definition}
\if@english
  % 定理・定義環境(amsthm)
  \newtheorem{definition}{Definition}
  \newtheorem{theorem}{Theorem}
  \newtheorem{corollary}{Corollary}
  \newtheorem{lemma}{Lemma}
\else
  % 定理・定義環境(amsthm)
  \newtheorem{definition}{定義}
  \newtheorem{theorem}{定理}
  \newtheorem{corollary}{系}
  \newtheorem{lemma}{補題}
\fi

\endinput