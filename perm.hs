module Main where

import Control.Concurrent.Async (mapConcurrently)
import Data.List (permutations, maximumBy)
import Data.Ord (comparing)
import Data.Set (Set)
import qualified Data.Set as Set
import System.IO

data Perm = Perm [Int] deriving (Eq, Ord, Show)

instance Semigroup Perm where
  Perm p1 <> Perm p2 = Perm [p1 !! i | i <- p2]

allPerms :: Int -> [Perm]
allPerms n = map Perm (permutations [0..n-1])

findCover2 :: [Perm] -> IO [Perm]
findCover2 universe = go [] Set.empty
  where
    uSet = Set.fromList universe
    go :: [Perm] -> Set Perm -> IO [Perm]
    go !a !covered
      | covered == uSet = return a
      | otherwise = do
        let unused = filter (`notElem` a) universe
        scored <- mapConcurrently (\x -> let newCov = coverWith x a covered in return (x, Set.size newCov)) unused
        let best = fst $ maximumBy (comparing snd) scored
            covered' = coverWith best a covered
        (putStrLn $ "Covered " ++ show (Set.size covered') ++ "/" ++ show (Set.size uSet) ++ " | Cover size: " ++ show (length a + 1))
        go (best:a) covered'
    coverWith :: Perm -> [Perm] -> Set Perm -> Set Perm
    coverWith x a covered =
      let partners = x : a
          prods1   = [ x <> y | y <- partners ]
          prods2   = [ y <> x | y <- partners ]
      in covered `Set.union` Set.fromList (prods1 ++ prods2)

main :: IO ()
main =
  let universe = allPerms 8
  in hSetBuffering stdout NoBuffering >> findCover2 universe >>= print

