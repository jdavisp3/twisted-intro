#!/usr/bin/env escript
%% -*- erlang -*-
%%! -smp enable

-mode(compile).


usage() ->
    io:format("usage: get-poetry [hostname]:port ...

This is the Get Poetry Now! client, Erlang Edition.
Run it like this:

  get-poetry port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  erlang-client/get-poetry 10001 10002 10003

to grab poetry from servers on ports 10001, 10002, and 10003.

Of course, there need to be servers listening on those ports
for that to work.
"),
    halt(1).


parse_args(Args) ->
    try
        [parse_addr(Arg) || Arg <- Args]
    catch
        _:_ ->
            usage()
    end.


parse_addr(Addr) ->
    parse_addr(Addr, []).

parse_addr([], Accum) ->
    {"localhost", erlang:list_to_integer(lists:reverse(Accum))};
parse_addr([$:|Addr], Accum) ->
    {lists:reverse(Accum), erlang:list_to_integer(Addr)};
parse_addr([Ch|Addr], Accum) ->
    parse_addr(Addr, [Ch|Accum]).


enumerate(L) ->
    enumerate(L, 1).

enumerate([], _) ->
    [];
enumerate([X|Xs], N) ->
    [{N, X} | enumerate(Xs, N+1)].


collect_poems(0, Poems) ->
    [io:format("~s\n", [P]) || P <- Poems];
collect_poems(N, Poems) ->
    receive
        {'DOWN', _, _, _, _} ->
            collect_poems(N-1, Poems);
        {poem, Poem} ->
            collect_poems(N, [Poem|Poems])
    end.


peername(Socket) ->
    {ok, {IP, Port}} = inet:peername(Socket),
    format_ip(IP) ++ ":" ++ erlang:integer_to_list(Port).

format_ip(IP) when is_tuple(IP) ->
    format_ip(erlang:tuple_to_list(IP));
format_ip(IP) ->
    string:join([erlang:integer_to_list(N) || N <- IP], ":").


get_poetry(Tasknum, Addr, Main) ->
    {Host, Port} = Addr,
    {ok, Socket} = gen_tcp:connect(Host, Port,
                                   [binary, {active, false}, {packet, 0}]),
    get_poetry(Tasknum, Socket, Main, []).

get_poetry(Tasknum, Socket, Main, Packets) ->
    case gen_tcp:recv(Socket, 0) of
        {ok, Packet} ->
            io:format("Task ~w: got ~w bytes of poetry from ~s\n",
                      [Tasknum, size(Packet), peername(Socket)]),
            get_poetry(Tasknum, Socket, Main, [Packet|Packets]);
        {error, _} ->
            Main ! {poem, list_to_binary(lists:reverse(Packets))}
    end.


main([]) ->
    usage();

main(Args) ->
    Addresses = parse_args(Args),
    Main = self(),
    [erlang:spawn_monitor(fun () -> get_poetry(TaskNum, Addr, Main) end)
     || {TaskNum, Addr} <- enumerate(Addresses)],
    collect_poems(length(Addresses), []).
