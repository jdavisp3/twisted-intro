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
import Control.Exception

data Task =
    Task { taskNum :: Int,
           taskHostname :: HostName,
           taskPort :: PortNumber }
    deriving (Show)


parseServer :: String -> (HostName, PortNumber)
parseServer arg
    | ':' `elem` arg = (host, to_port portstr)
    | otherwise = ("localhost", to_port arg)
    where
      (host, (_:portstr)) = break ((==) ':') arg
      to_port = fromIntegral . (read :: String -> Integer)

makeTasks :: [String] -> [Task]
makeTasks args = zipWith makeTask args [1..]
    where
      makeTask arg num =
          let (host, port) = parseServer arg
          in Task { taskNum = num,
                    taskHostname = host,
                    taskPort = port }

getPoetry :: Handle -> Task -> IO ()
getPoetry h task = do
  -- it looks like we read the whole poem here, but Haskell is lazy,
  -- like Python generators, or some programmers you may know
  poem <- hGetContents h
  mapM_ gotLine $ lines poem
  putStrLn poem
  where
    prefix = "Task " ++ (show $ taskNum task) ++ ": got "
    suffix = concat [" bytes of poetry from ",
                     (taskHostname task), ":",
                     (show $ taskPort task)]
    gotLine line =
        putStrLn $ prefix ++ (show numbytes) ++ suffix
        where numbytes = (length line) + 1

runTask :: Task -> IO (MVar ())
runTask task = do
  h <- connectTo (taskHostname task) (PortNumber $ taskPort task)

  mvar <- newEmptyMVar

  -- read each poem in a Haskell lightweight thread
  _ <- forkIO $ getPoetry h task `finally` putMVar mvar ()

  return mvar

main :: IO ()
main = do
  args <- getArgs
  mvars <- mapM runTask $ makeTasks args
  mapM_ takeMVar mvars -- wait for all the threads to finish
