{-
A Get Poetry Now! client in Haskell.

Avert your eyes, I don't really know what I'm doing.
This just illustrates Haskell's use of asynchronous IO.

To build the program, run this:

  ghc --make get-poetry.hs

Then run it like this:

  ./get-poetry 10000 10001 10002

You'll need to have poetry servers running on those ports, of course.
-}

import Network
import System.IO
import System.Environment
import Control.Concurrent

parseServer :: String -> (HostName, PortNumber)
parseServer arg
    | ':' `elem` arg = (host, to_port portstr)
    | otherwise = ("localhost", to_port arg)
    where
      (host, (_:portstr)) = break ((==) ':') arg
      to_port = fromIntegral . (read :: String -> Integer)

getPoem :: (HostName, PortNumber) -> IO (MVar String)
getPoem (host, port) = do
  mvar <- newEmptyMVar
  _ <- forkIO (do h <- connectTo host (PortNumber $ port)
                  poem <- hGetContents h
                  putMVar mvar poem)
  return mvar

main :: IO ()
main = do
  args <- getArgs
  mvars <- mapM getPoem (map parseServer args)
  mapM_ (\mvar -> do poem <- takeMVar mvar
                     putStrLn poem) mvars
