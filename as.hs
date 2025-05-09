{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE CPP #-}

module Main where

import Data.Bits
import qualified Data.ByteString as BS
import qualified Data.ByteString.Builder as BB
import Data.Word
import Numeric (showHex)
import System.Environment (getArgs)
import System.Exit (exitFailure)
import Text.Parsec
import Text.Printf (printf)

-- TYPES

newtype Sreg = Sreg Word8 -- Scalar register

newtype Vreg = Vreg Word8 -- Vector register

newtype Imm8 = Imm8 Word8 -- 8-bit value

newtype Imm16 = Imm16 Word16 -- 16-bit value

newtype Mem = Mem (Sreg, Imm8) -- memory address (ie. [S1 + imm8])

data MOV
  = SCALARMOV_RR Sreg Sreg -- mov s1, s2
  | SCALARMOV_RM Sreg Mem -- mov s1, [s2 + imm8]
  | SCALARMOV_MR Mem Sreg -- mov [s1 + imm8], s2
  | SCALARMOV_RI Sreg Imm16 -- mov s1, imm8
  | VECTORPERM Vreg Vreg Imm8 -- mov v1, v2, perm OR mov v1, v2
  | VECTORMOV_RM Vreg Mem -- mov v1, [s2 + imm8]
  | VECTORMOV_MR Mem Vreg -- mov [s1 + imm8], v2
  | BROADCAST Vreg Sreg Imm8 -- mov v1, s2, imm8 OR mov v1, s2

data ALU
  = SADD Sreg Sreg Sreg -- add s1, s2, s3
  | SMUL Sreg Sreg Sreg -- mul s1, s2, s3
  | SNEG Sreg Sreg -- neg s1, s2
  | SDIV Sreg Sreg Sreg -- div s1, s2, s3
  | SAND Sreg Sreg Sreg -- and s1, s2, s3
  | SOR Sreg Sreg Sreg -- or s1, s2, s3
  | SXOR Sreg Sreg Sreg -- xor s1, s2, s3
  | SNOT Sreg Sreg -- not s1, s2
  | VADD Vreg Vreg Vreg -- add v1, v2, v3
  | VMUL Vreg Vreg Vreg -- mul v1, v2, v3
  | VNEG Vreg Vreg -- neg v1, v2
  | VDIV Vreg Vreg Vreg -- div v1, v2, v3
  | VAND Vreg Vreg Vreg -- and v1, v2, v3
  | VOR Vreg Vreg Vreg -- or v1, v2, v3
  | VXOR Vreg Vreg Vreg -- xor v1, v2, v3
  | VNOT Vreg Vreg -- not v1, v2

data Instruction
  = MOV MOV
  | ALU ALU

#ifdef ANSICOLOR
instance Show Sreg where show (Sreg s) = "\x1b[32ms" ++ show s ++ "\x1b[0m"
instance Show Vreg where show (Vreg v) = "\x1b[34mv" ++ show v ++ "\x1b[0m"
instance Show Imm8 where show (Imm8 i) = "\x1b[35m0x" ++ showHex i "" ++ "\x1b[0m"
instance Show Imm16 where show (Imm16 i) = "\x1b[35m0x" ++ showHex i "" ++ "\x1b[0m"
#else
instance Show Sreg where show (Sreg s) = "s" ++ show s
instance Show Vreg where show (Vreg v) = "v" ++ show v
instance Show Imm8 where show (Imm8 i) = "0x" ++ showHex i ""
instance Show Imm16 where show (Imm16 i) = "0x" ++ showHex i ""
#endif

instance Show Mem where show (Mem (Sreg s, Imm8 i)) = "[" ++ show s ++ " + " ++ show i ++ "]"

instance Show MOV where
#ifdef ANSICOLOR
  show m = "\x1b[33mmov\x1b[0m " ++ case m of
#else
  show m = "mov " ++ case m of
#endif
    SCALARMOV_RR s1 s2 -> show s1 ++ ", " ++ show s2
    SCALARMOV_RM s1 m -> show s1 ++ ", " ++ show m
    SCALARMOV_MR m s2 -> show m ++ ", " ++ show s2
    SCALARMOV_RI s1 i -> show s1 ++ ", " ++ show i
    VECTORPERM v1 v2 i -> show v1 ++ ", " ++ show v2 ++ ", " ++ show i
    VECTORMOV_RM v1 m -> show v1 ++ ", " ++ show m
    VECTORMOV_MR m v2 -> show m ++ ", " ++ show v2
    BROADCAST v1 s2 i -> show v1 ++ ", " ++ show s2 ++ ", " ++ show i

instance Show ALU where
#ifdef ANSICOLOR
  show a = "\x1b[33m" ++ case a of
#else
  show a = case a of
#endif
    SADD s1 s2 s3 -> "add " ++ show s1 ++ ", " ++ show s2 ++ ", " ++ show s3
    SMUL s1 s2 s3 -> "mul " ++ show s1 ++ ", " ++ show s2 ++ ", " ++ show s3
    SNEG s1 s2 -> "neg " ++ show s1 ++ ", " ++ show s2
    SDIV s1 s2 s3 -> "div " ++ show s1 ++ ", " ++ show s2 ++ ", " ++ show s3
    SAND s1 s2 s3 -> "and " ++ show s1 ++ ", " ++ show s2 ++ ", " ++ show s3
    SOR s1 s2 s3 -> "or " ++ show s1 ++ ", " ++ show s2 ++ ", " ++ show s3
    SXOR s1 s2 s3 -> "xor " ++ show s1 ++ ", " ++ show s2 ++ ", " ++ show s3
    SNOT s1 s2 -> "not " ++ show s1 ++ ", " ++ show s2
    VADD v1 v2 v3 -> "add " ++ show v1 ++ ", " ++ show v2 ++ ", " ++ show v3
    VMUL v1 v2 v3 -> "mul " ++ show v1 ++ ", " ++ show v2 ++ ", " ++ show v3
    VNEG v1 v2 -> "neg " ++ show v1 ++ ", " ++ show v2
    VDIV v1 v2 v3 -> "div " ++ show v1 ++ ", " ++ show v2 ++ ", " ++ show v3
    VAND v1 v2 v3 -> "and " ++ show v1 ++ ", " ++ show v2 ++ ", " ++ show v3
    VOR v1 v2 v3 -> "or " ++ show v1 ++ ", " ++ show v2 ++ ", " ++ show v3
    VXOR v1 v2 v3 -> "xor " ++ show v1 ++ ", " ++ show v2 ++ ", " ++ show v3
    VNOT v1 v2 -> "not " ++ show v1 ++ ", " ++ show v2

instance Show Instruction where
  show (MOV m) = show m
  show (ALU a) = show a

-- PARSING

symbol :: Char -> Parsec String () Char
symbol c = spaces *> char c <* spaces

sreg :: Parsec String () Sreg
sreg = char 's' >> (Sreg . read <$> many1 digit)

vreg :: Parsec String () Vreg
vreg = char 'v' >> (Vreg . read <$> many1 digit)

imm8 :: Parsec String () Imm8
imm8 = Imm8 . read <$> (try (string "0x" <> many1 hexDigit) <|> many digit)

imm16 :: Parsec String () Imm16
imm16 = Imm16 . read <$> (try (string "0x" <> many1 hexDigit) <|> many digit)

mem :: Parsec String () Mem
mem = Mem <$> (symbol '[' *> liftA2 (,) sreg (symbol '+' *> imm8) <* symbol ']')

mov :: Parsec String () MOV
mov =
  string "mov"
    *> spaces
    *> ( try (SCALARMOV_RR <$> sreg <* symbol ',' <*> sreg)
           <|> try (SCALARMOV_RM <$> sreg <* symbol ',' <*> mem)
           <|> try (SCALARMOV_MR <$> mem <* symbol ',' <*> sreg)
           <|> try (SCALARMOV_RI <$> sreg <* symbol ',' <*> imm16)
           <|> try (VECTORPERM <$> vreg <* symbol ',' <*> vreg <*> (pure . Imm8) 0)
           <|> try (VECTORPERM <$> vreg <* symbol ',' <*> vreg <* symbol ',' <*> imm8)
           <|> try (VECTORMOV_RM <$> vreg <* symbol ',' <*> mem)
           <|> try (VECTORMOV_MR <$> mem <* symbol ',' <*> vreg)
           <|> try (BROADCAST <$> vreg <* symbol ',' <*> sreg <*> (pure . Imm8) 0xFF)
           <|> (BROADCAST <$> vreg <* symbol ',' <*> sreg <* symbol ',' <*> imm8)
       )

alu :: Parsec String () ALU
alu = choice (map try (init ops) ++ [last ops])
  where
    ops =
      [ string "add" *> spaces *> try (instr3 sreg SADD <|> instr3 vreg VADD),
        string "mul" *> spaces *> try (instr3 sreg SMUL <|> instr3 vreg VMUL),
        string "neg" *> spaces *> try (instr2 sreg SNEG <|> instr2 vreg VNEG),
        string "div" *> spaces *> try (instr3 sreg SDIV <|> instr3 vreg VDIV),
        string "and" *> spaces *> try (instr3 sreg SAND <|> instr3 vreg VAND),
        string "or" *> spaces *> try (instr3 sreg SOR <|> instr3 vreg VOR),
        string "xor" *> spaces *> try (instr3 sreg SXOR <|> instr3 vreg VXOR),
        string "not" *> spaces *> try (instr2 sreg SNOT <|> instr2 vreg VNOT)
      ]

    instr2 p c = c <$> p <* symbol ',' <*> p
    instr3 p c = c <$> p <* symbol ',' <*> p <* symbol ',' <*> p

instr :: Parsec String () Instruction
instr = MOV <$> mov <|> ALU <$> alu

-- ENCODING

construct :: Word8 -> Word8 -> Word8 -> Word8 -> Word32
construct a b c d = fromIntegral a .<<. 24 .|. fromIntegral b .<<. 16 .|. fromIntegral c .<<. 8 .|. fromIntegral d

encode :: Instruction -> Word32
encode (MOV (SCALARMOV_RR (Sreg s1) (Sreg s2))) = construct 0b00000_000 s1 s2 0
encode (MOV (SCALARMOV_RM (Sreg s1) (Mem (Sreg s2, Imm8 i)))) = construct 0b00000_001 s1 s2 i
encode (MOV (SCALARMOV_MR (Mem (Sreg s1, Imm8 i)) (Sreg s2))) = construct 0b00000_010 s1 i s2
encode (MOV (SCALARMOV_RI (Sreg s1) (Imm16 i))) = construct 0b00000_011 s1 (fromIntegral i .>>. 8) (fromIntegral i)
encode (MOV (VECTORPERM (Vreg v1) (Vreg v2) (Imm8 i))) = construct 0b00000_100 v1 v2 i
encode (MOV (VECTORMOV_RM (Vreg v1) (Mem (Sreg s2, Imm8 i)))) = construct 0b00000_101 v1 s2 i
encode (MOV (VECTORMOV_MR (Mem (Sreg s1, Imm8 i)) (Vreg v2))) = construct 0b00000_110 s1 i v2
encode (MOV (BROADCAST (Vreg v1) (Sreg s2) (Imm8 i))) = construct 0b00000_111 v1 s2 i
encode (ALU (SADD (Sreg s1) (Sreg s2) (Sreg s3))) = construct 0b00001_000 s1 s2 s3
encode (ALU (SMUL (Sreg s1) (Sreg s2) (Sreg s3))) = construct 0b00001_001 s1 s2 s3
encode (ALU (SNEG (Sreg s1) (Sreg s2))) = construct 0b00001_010 s1 s2 0
encode (ALU (SDIV (Sreg s1) (Sreg s2) (Sreg s3))) = construct 0b00001_011 s1 s2 s3
encode (ALU (SAND (Sreg s1) (Sreg s2) (Sreg s3))) = construct 0b00001_100 s1 s2 s3
encode (ALU (SOR (Sreg s1) (Sreg s2) (Sreg s3))) = construct 0b00001_101 s1 s2 s3
encode (ALU (SXOR (Sreg s1) (Sreg s2) (Sreg s3))) = construct 0b00001_110 s1 s2 s3
encode (ALU (SNOT (Sreg s1) (Sreg s2))) = construct 0b00001_111 s1 s2 0
encode (ALU (VADD (Vreg v1) (Vreg v2) (Vreg v3))) = construct 0b00010_000 v1 v2 v3
encode (ALU (VMUL (Vreg v1) (Vreg v2) (Vreg v3))) = construct 0b00010_001 v1 v2 v3
encode (ALU (VNEG (Vreg v1) (Vreg v2))) = construct 0b00010_010 v1 v2 0
encode (ALU (VDIV (Vreg v1) (Vreg v2) (Vreg v3))) = construct 0b00010_011 v1 v2 v3
encode (ALU (VAND (Vreg v1) (Vreg v2) (Vreg v3))) = construct 0b00010_100 v1 v2 v3
encode (ALU (VOR (Vreg v1) (Vreg v2) (Vreg v3))) = construct 0b00010_101 v1 v2 v3
encode (ALU (VXOR (Vreg v1) (Vreg v2) (Vreg v3))) = construct 0b00010_110 v1 v2 v3
encode (ALU (VNOT (Vreg v1) (Vreg v2))) = construct 0b00010_111 v1 v2 0

-- DECODING

decode :: Word8 -> Word8 -> Word8 -> Word8 -> Instruction
decode a b c d = case a of
  0b00000_000 -> MOV (SCALARMOV_RR (Sreg b) (Sreg c))
  0b00000_001 -> MOV (SCALARMOV_RM (Sreg b) (Mem (Sreg c, Imm8 d)))
  0b00000_010 -> MOV (SCALARMOV_MR (Mem (Sreg b, Imm8 c)) (Sreg d))
  0b00000_011 -> MOV (SCALARMOV_RI (Sreg b) (Imm16 ((fromIntegral c .<<. 8) .|. fromIntegral d)))
  0b00000_100 -> MOV (VECTORPERM (Vreg b) (Vreg c) (Imm8 d))
  0b00000_101 -> MOV (VECTORMOV_RM (Vreg b) (Mem (Sreg c, Imm8 d)))
  0b00000_110 -> MOV (VECTORMOV_MR (Mem (Sreg b, Imm8 c)) (Vreg d))
  0b00000_111 -> MOV (BROADCAST (Vreg b) (Sreg c) (Imm8 d))
  0b00001_000 -> ALU (SADD (Sreg b) (Sreg c) (Sreg d))
  0b00001_001 -> ALU (SMUL (Sreg b) (Sreg c) (Sreg d))
  0b00001_010 -> ALU (SNEG (Sreg b) (Sreg c))
  0b00001_011 -> ALU (SDIV (Sreg b) (Sreg c) (Sreg d))
  0b00001_100 -> ALU (SAND (Sreg b) (Sreg c) (Sreg d))
  0b00001_101 -> ALU (SOR (Sreg b) (Sreg c) (Sreg d))
  0b00001_110 -> ALU (SXOR (Sreg b) (Sreg c) (Sreg d))
  0b00001_111 -> ALU (SNOT (Sreg b) (Sreg c))
  0b00010_000 -> ALU (VADD (Vreg b) (Vreg c) (Vreg d))
  0b00010_001 -> ALU (VMUL (Vreg b) (Vreg c) (Vreg d))
  0b00010_010 -> ALU (VNEG (Vreg b) (Vreg c))
  0b00010_011 -> ALU (VDIV (Vreg b) (Vreg c) (Vreg d))
  0b00010_100 -> ALU (VAND (Vreg b) (Vreg c) (Vreg d))
  0b00010_101 -> ALU (VOR (Vreg b) (Vreg c) (Vreg d))
  0b00010_110 -> ALU (VXOR (Vreg b) (Vreg c) (Vreg d))
  0b00010_111 -> ALU (VNOT (Vreg b) (Vreg c))
  _ -> error "Invalid instruction"

-- MAIN

usage :: IO ()
usage = putStrLn "usage: simd as <input file> <output file>\n       simd objdump <input file>" >> exitFailure

main :: IO ()
main =
  getArgs >>= \case
    ["as", i, o] ->
      readFile i >>= \s -> case parse (many1 (instr <* symbol ';')) i s of
        Left err -> print err >> exitFailure
        Right is -> BB.writeFile o (mconcat (map (BB.word32BE . encode) is))
    ["objdump", i] ->
      BS.readFile i >>= mapM_ (\(i, (a, b, c, d)) -> printf "%8d:\t%08b %02x %02x %02x\t%s\n" i a b c d (show (decode a b c d))) . zip [0 :: Integer ..] . chunk4 . BS.unpack
      where
        chunk4 :: [Word8] -> [(Word8, Word8, Word8, Word8)]
        chunk4 [] = []
        chunk4 (a : b : c : d : t) = (a, b, c, d) : chunk4 t
        chunk4 _ = error "Invalid input file"
    _ -> usage
