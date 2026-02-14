#!/bin/bash
set -e

BRANCH=$1
MODE=$2
MSG=$3
TARGET="main"

# Validation
if [ "$BRANCH" = "$TARGET" ]; then
    echo "❌ Error: You are on $TARGET branch."
    exit 1
fi

case $MODE in
    "sync")
        echo "🔄 Updating $TARGET and merging into $BRANCH..."
        git checkout $TARGET && git pull origin $TARGET
        git checkout "$BRANCH"
        git merge $TARGET --no-edit
        echo "✅ Sync complete. Fix conflicts if any."
        ;;

    "merge")
        [ -z "$MSG" ] && { echo "💬 Error: Missing message (m='msg')"; exit 1; }
        echo "🔗 Local squash-merge into $TARGET..."
        git checkout $TARGET && git pull origin $TARGET
        git merge --squash "$BRANCH"
        git commit -m "$MSG"
        git branch -D "$BRANCH"
        echo "✅ Merged locally into $TARGET."
        ;;

    "push")
        echo "📤 Pushing $BRANCH to origin..."
        git push origin "$BRANCH"
        echo "✅ Pushed safely."
        ;;

    "ship")
        echo "🚀 Full workflow: Sync + Push + PR..."
        # Sync
        git checkout $TARGET && git pull origin $TARGET
        git checkout "$BRANCH" && git merge $TARGET --no-edit
        # Push
        git push origin "$BRANCH"
        # PR (Requires GitHub CLI 'gh')
        gh pr create --base $TARGET --head "$BRANCH" --fill --web || echo "⚠️  PR creation failed. Do it manually."
        ;;
    *)
        echo "❌ Unknown mode: $MODE"
        exit 1
        ;;
esac