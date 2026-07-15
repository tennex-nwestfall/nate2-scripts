_bing_wrapper() {
  local -a bing_args
  local -i double_dash_pos=0

  # Find position of "--"
  for (( i=1; i <= $#words; i++ )); do
    if [[ "${words[$i]}" == "--" ]]; then
      double_dash_pos=$i
      break
    fi
  done

  if (( double_dash_pos > 0 && CURRENT > double_dash_pos )); then
    # Delegate to the wrapped command's completion
    words=("${words[@]:$double_dash_pos}")
    CURRENT=$(( CURRENT - double_dash_pos ))
    _normal  # let zsh look up the right completion for inner_cmd
  else
    # Complete bing-wrapper's own options
      _arguments \
      '--end[play sound at end]' \
      '*--pattern[pattern to listen for]:pattern:' \
      '--sound-end[sound file at end]:file:_files' \
      '--sound-pattern[sound file for pattern]:file:_files' \
      '--[inner command]:command:_normal' 
  fi
}

compdef _bing_wrapper bing-wrapper