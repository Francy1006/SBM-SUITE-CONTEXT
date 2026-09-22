#!/usr/bin/env bash

context_deploy_is_lifecycle_phase() {
  case "$1" in
    planning-activation|objective-activation|objective-registration|objective-completion|objective-deletion|objective-update|implementation-progress|implementation-closure)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

context_deploy_parse_args() {
  if [[ "$#" -ge 2 ]] && context_deploy_is_lifecycle_phase "$1"; then
    [[ "$#" -le 3 ]] || return 1
    PROJECT_NAME="sbm-suite-context"
    LIFECYCLE_PHASE="$1"
    OBJECTIVES_SOURCE="$2"
    USER_PROMPT="${3:-}"
    return 0
  fi

  [[ "$#" -ge 3 && "$#" -le 4 ]] || return 1
  PROJECT_NAME="$1"
  LIFECYCLE_PHASE="$2"
  OBJECTIVES_SOURCE="$3"
  USER_PROMPT="${4:-}"
}
