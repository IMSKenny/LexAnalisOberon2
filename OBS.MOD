MODULE OBS;  (*NW 7.6.87 / 18.3.93*)

   IMPORT Reals, Texts, Oberon;

   (*symbols:
       |  0          1          2           3            4
    ---|--------------------------------------------------------
     0 |  null       *          /           DIV          MOD
     5 |  &          +          -           OR           =
    10 |  #          <          <=          >            >=
    15 |  IN         IS         ^           .            ,
    20 |  :          ..         )           ]            }
    25 |  OF         THEN       DO          TO           (
    30 |  [          {          ~           :=           number
    35 |  NIL        string     ident       ;            |
    40 |  END        ELSE       ELSIF       UNTIL        IF
    45 |  CASE       WHILE      REPEAT      LOOP         WITH      
    50 |  EXIT       RETURN     FOR         BY          ARRAY
    55 |  RECORD       POINTER     BEGIN      CONST      TYPE
    60 |  VAR          PROCEDURE  IMPORT     MODULE     eof *)

   CONST KW = 47;  (*size of hash table*)
            maxDig = 32;
            maxExp = 308;
            maxStrLen = 128;

   (*name, numtyp, intval, realval, lrlval are implicit results of Get*)

   VAR numtyp* : INTEGER; (* 1 = char, 2 = integer, 3 = real, 4 = longreal*)
      intval* : LONGINT;
      realval*: REAL;
      lrlval* : LONGREAL;
      scanerr*: BOOLEAN;
      name*   : ARRAY maxStrLen OF CHAR;

      R: Texts.Reader;
      W: Texts.Writer;

      ch, prev: CHAR;     (*current and previous  characters*)
      lastpos: LONGINT; (*error position in source file*)

      i: INTEGER;
      keyTab  : ARRAY KW OF
                        RECORD symb, alt: INTEGER; id: ARRAY 12 OF CHAR END;

   PROCEDURE Mark*(n: INTEGER);
      VAR pos: LONGINT;
   BEGIN pos := Texts.Pos(R);
      IF lastpos + 8 < pos THEN
         Texts.WriteLn(W); Texts.WriteString(W, "  pos");
         Texts.WriteInt(W, pos, 6);
         IF n < 0 THEN Texts.WriteString(W, "  warning")
         ELSE Texts.WriteString(W, "  err"); scanerr := TRUE; lastpos := pos
         END ;
         Texts.WriteInt(W, ABS(n), 4); Texts.Append(Oberon.Log, W.buf)
      END
   END Mark;

   PROCEDURE String(VAR sym: INTEGER);
      VAR i: INTEGER;
   BEGIN i := 0;
      LOOP
         IF ch = 22X THEN EXIT END ;
         IF ch < " " THEN Mark(3); EXIT END ;
         IF i < maxStrLen-1 THEN name[i] := ch; INC(i) ELSE Mark(212); i := 0 END ;
         Texts.Read(R, ch)
      END ;
      Texts.Read(R, ch);
      IF i = 1 THEN sym := 34; numtyp := 1; intval := ORD(name[0])
      ELSE sym := 36; name[i] := 0X (*string*)
      END
   END String;

   PROCEDURE Identifier(VAR sym: INTEGER);
      VAR i, k: INTEGER;
   BEGIN name[0] := prev; i := 1; k := ORD(prev);
      WHILE (CAP(ch) >= "A") & (CAP(ch) <= "Z") OR (ch >= "0") & (ch <= "9") DO
         IF i < 31 THEN name[i] := ch; INC(i); INC(k, ORD(ch)) END ;
         Texts.Read(R, ch)
      END ;
      name[i] := 0X;
      k := (k+i) MOD KW;  (*hash function*)
      IF (keyTab[k].symb # 0) & (keyTab[k].id = name) THEN sym := keyTab[k].symb
      ELSE k := keyTab[k].alt;
         IF (keyTab[k].symb # 0) & (keyTab[k].id = name) THEN sym := keyTab[k].symb
         ELSE sym := 37 (*ident*)
         END
      END
   END Identifier;

   PROCEDURE Number;
      VAR i, j, c, e, s: INTEGER;
         k: LONGINT;
         x: LONGREAL;
         lastCh, expch: CHAR;
         negE, hex: BOOLEAN;
         d: ARRAY maxDig OF INTEGER;
   BEGIN c := ORD(prev) - 30H; hex := FALSE; i := 0;
      LOOP d[i] := c; INC(i);
         IF ch < "0" THEN EXIT END ;
         IF ch <= "9" THEN c := ORD(ch) - 30H
         ELSIF ("A" <= ch) & (ch <= "F") THEN c := ORD(ch) - 37H; hex := TRUE
         ELSE EXIT
         END ;
         Texts.Read(R, ch)
      END ;
      lastCh := ch; j := 0; k := 0;
      IF ch = "." THEN Texts.Read(R, ch);
         IF ch = "." THEN lastCh := 0X; ch := 7FX END
      END ;
      IF lastCh = "." THEN (*decimal point*)
         IF hex THEN Mark(2) END ;
         x := 0; e := 0;
         REPEAT x := x * 10 + d[j]; INC(j) UNTIL j = i;  (*integer part*)
         WHILE ("0" <= ch) & (ch <= "9") DO
            x := x * 10 + (ORD(ch) - 30H); DEC(e); Texts.Read(R, ch)  (*fraction*)
         END ;
         expch := ch;
         IF (ch = "E") OR (ch = "D") THEN  (*scale factor*)
            s := 0; Texts.Read(R, ch);
            IF ch = "-" THEN negE := TRUE; Texts.Read(R, ch)
            ELSE negE := FALSE;
               IF ch = "+" THEN Texts.Read(R, ch) END
            END ;
            IF ("0" <= ch) & (ch <= "9") THEN
               REPEAT s := s*10 + ORD(ch)-30H; Texts.Read(R, ch)
               UNTIL (ch < "0") OR (ch >"9");
               IF negE THEN DEC(e, s) ELSE INC(e, s) END
            ELSE Mark(2)
            END
         END ;
         IF e < 0 THEN
            IF e >= -maxExp THEN x := x / Reals.TenL(-e) ELSE x := 0 END
         ELSIF e > 0 THEN
            IF e <= maxExp THEN x := Reals.TenL(e) * x ELSE x := 0; Mark(203) END
         END ;
         IF expch = "D" THEN numtyp := 4; lrlval := x
         ELSE numtyp := 3;
            IF x <= MAX(REAL) THEN realval := SHORT(x) ELSE x := 0; Mark(203) END
         END
      ELSIF lastCh = "H" THEN
         Texts.Read(R, ch);
         WHILE d[j] = 0 DO INC(j) END ;
         IF i-j <= 8 THEN
            IF (i-j = 8) & (d[j] >= 8) THEN DEC(d[j], 16) END ;
            WHILE j < i DO k := k * 10H + d[j]; INC(j) END
         ELSE Mark(203)
         END ;
         numtyp := 2; intval := k
      ELSIF lastCh = "X" THEN
         Texts.Read(R, ch);
         WHILE j < i DO
            k := k * 10H + d[j]; INC(j);
            IF k > 0FFH THEN Mark(203); k := 0 END
         END ;
         numtyp := 1; intval := k
      ELSE (*decimal integer*)
         IF hex THEN Mark(2) END ;
         WHILE j < i DO
            IF k <= (MAX(LONGINT) - d[j]) DIV 10 THEN k := k*10 + d[j]
            ELSE Mark(203); k := 0
            END ;
            INC(j)
         END ;
         numtyp := 2; intval := k
      END
   END Number;

   PROCEDURE Get*(VAR sym: INTEGER);
      VAR s: INTEGER;

      PROCEDURE Comment;   (* do not read after end of file *)
      BEGIN Texts.Read(R, ch);
         LOOP
            LOOP
               WHILE ch = "(" DO Texts.Read(R, ch);
                  IF ch = "*" THEN Comment END
               END ;
               IF ch = "*" THEN Texts.Read(R, ch); EXIT END ;
               IF ch = 0X THEN EXIT END ;
               Texts.Read(R, ch)
            END ;
            IF ch = ")" THEN Texts.Read(R, ch); EXIT END ;
            IF ch = 0X THEN Mark(5); EXIT END
         END
      END Comment;

   BEGIN
      LOOP (*ignore control characters*)
         IF ch <= " " THEN
            IF ch = 0X THEN ch := " "; EXIT
            ELSE Texts.Read(R, ch)
            END
         ELSIF ch > 7FX THEN Texts.Read(R, ch)
         ELSE EXIT
         END
      END ;
      prev := ch; Texts.Read(R, ch);
      CASE prev OF   (* " " <= prev <= 7FX *)
            " "  : s := 62; ch := 0X (*eof*)
         | "!", "$", "%", "'", "?", "@", "\", "_", "`": s :=  0
         | 22X  : String(s)
         | "#"  : s := 10
         | "&"  : s :=  5
         | "("  : IF ch = "*" THEN Comment; Get(s) ELSE s := 29 END
         | ")"  : s := 22
         | "*"  : s :=  1
         | "+"  : s :=  6
         | ","  : s := 19
         | "-"  : s :=  7
         | "."  : IF ch = "." THEN Texts.Read(R, ch); s := 21 ELSE s := 18 END
         | "/"  : s := 2
         | "0".."9": Number; s := 34
         | ":"  : IF ch = "=" THEN Texts.Read(R, ch); s := 33 ELSE s := 20 END
         | ";"  : s := 38
         | "<"  : IF ch = "=" THEN Texts.Read(R, ch); s := 12 ELSE s := 11 END
         | "="  : s :=  9
         | ">"  : IF ch = "=" THEN Texts.Read(R, ch); s := 14 ELSE s := 13 END
         | "A".."Z": Identifier(s)
         | "["  : s := 30
         | "]"  : s := 23
         | "^"  : s := 17
         | "a".."z": Identifier(s)
         | "{"  : s := 31
         | "|"  : s := 39
         | "}"  : s := 24
         | "~"  : s := 32
         | 7FX  : s := 21
      END ;
      sym := s
   END Get;

   PROCEDURE Init*(source: Texts.Text; pos: LONGINT);
   BEGIN
      ch := " "; scanerr := FALSE; lastpos := -8;
      Texts.OpenReader(R, source, pos)
   END Init;

   PROCEDURE EnterKW(sym: INTEGER; name: ARRAY OF CHAR);
      VAR j, k: INTEGER;
   BEGIN j := 0; k := 0;
      REPEAT INC(k, ORD(name[j])); INC(j)
      UNTIL name[j] = 0X;
      k := (k+j) MOD KW;  (*hash function*)
      IF keyTab[k].symb # 0 THEN
         j := k;
         REPEAT INC(k) UNTIL keyTab[k].symb = 0;
         keyTab[j].alt := k
      END ;
      keyTab[k].symb := sym; COPY(name, keyTab[k].id)
   END EnterKW;

BEGIN Texts.OpenWriter(W); i := KW;
   WHILE i > 0 DO
      DEC(i); keyTab[i].symb := 0; keyTab[i].alt := 0
   END ;
   keyTab[0].id := "";
   EnterKW(53, "BY");
   EnterKW(27, "DO");
   EnterKW(44, "IF");
   EnterKW(15, "IN");
   EnterKW(16, "IS");
   EnterKW(25, "OF");
   EnterKW( 8, "OR");
   EnterKW(28, "TO");
   EnterKW(40, "END");
   EnterKW(52, "FOR");
   EnterKW( 4, "MOD");
   EnterKW(35, "NIL");
   EnterKW(60, "VAR");
   EnterKW(45, "CASE");
   EnterKW(41, "ELSE");
   EnterKW(50, "EXIT");
   EnterKW(26, "THEN");
   EnterKW(59, "TYPE");
   EnterKW(49, "WITH");
   EnterKW(54, "ARRAY");
   EnterKW(57, "BEGIN");
   EnterKW(58, "CONST");
   EnterKW(42, "ELSIF");
   EnterKW(62, "IMPORT");
   EnterKW(43, "UNTIL");
   EnterKW(46, "WHILE");
   EnterKW(55, "RECORD");
   EnterKW(47, "REPEAT");
   EnterKW(51, "RETURN");
   EnterKW(56, "POINTER");
   EnterKW(61, "PROCEDURE");
   EnterKW( 3, "DIV");
   EnterKW(48, "LOOP");
   EnterKW(63, "MODULE");
END OBS.
