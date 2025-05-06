from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from spotify_downloader import get_spotify_track_metadata, download_track
import os
import requests

TOKEN = "bot token"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 How to Use", callback_data='help')],
        [InlineKeyboardButton("🎵 Download Track", callback_data='download_info')],
        [
            InlineKeyboardButton("🚀 Join BotLand AI", url="https://t.me/botlandai"),
            InlineKeyboardButton("📱 Join TechBlog LK", url="https://t.me/techbloglk")
        ],
        [InlineKeyboardButton("👨‍💻 Contact Owner", url="https://t.me/hdjhhhhs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎧 *Welcome to Spotify Track Info Bot\\!*\n\n"
        "✨ I can help you get information and download links for Spotify tracks\\.\n"
        "🔽 Click the buttons below to get started\\!",
        reply_markup=reply_markup,
        parse_mode='MarkdownV2'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback=False):
    keyboard = [
        [InlineKeyboardButton("🎵 Download Track", callback_data='download_info')],
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📖 *How to use the bot:*\n\n"
        "1️⃣ Use /download command followed by Spotify track URL\n"
        "   Example: `/download https://open\\.spotify\\.com/track/\\.\\.\\.`\n\n"
        "2️⃣ Or simply send the Spotify track URL\n\n"
        "🎁 *I'll provide you with:*\n"
        "• 🎵 Track Information\n"
        "• 💿 Album Details\n"
        "• ⬇️ Download Link"
    )

    if is_callback:
        await update.callback_query.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        keyboard = [
            [InlineKeyboardButton("🔍 How to Use", callback_data='help')],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ Please provide a Spotify track URL after the command\\.\n"
            "Example: `/download https://open\\.spotify\\.com/track/\\.\\.\\.`",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
        return

    track_url = context.args[0]
    await process_spotify_url(update, track_url)

async def process_spotify_url(update, track_url):
    if "open.spotify.com/track/" not in track_url:
        await update.message.reply_text("❌ Please provide a valid Spotify track URL.")
        return

    status_message = await update.message.reply_text("🔄 Processing your request...")
    
    # Extract track ID from URL to use in callback data
    track_id = track_url.split("/track/")[1].split("?")[0]
    
    track_data = get_spotify_track_metadata(track_url)
    
    if track_data:
        # Create inline keyboard for download with shortened callback data
        keyboard = [
            [InlineKeyboardButton("⬇️ Download Track", callback_data=f'get_link_{track_id}')],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        info_text = (
            "🎵 *Track Information:*\n\n"
            f"🎧 *Title:* `{track_data['name']}`\n"
            f"👤 *Artist:* `{track_data['artist']}`\n"
            f"💿 *Album:* `{track_data['album_name']}`\n"
            f"👥 *Album Artist:* `{track_data['album_artist']}`\n"
            f"[🖼️ Cover Image]({track_data['cover_url']})"
        )
        
        await status_message.delete()
        await update.message.reply_photo(
            photo=track_data['cover_url'],
            caption=info_text,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    else:
        await status_message.edit_text("❌ Failed to get track information.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        await help_command(update, context, is_callback=True)
    elif query.data == 'start':
        # Add a new callback for returning to the start menu
        keyboard = [
            [InlineKeyboardButton("🔍 How to Use", callback_data='help')],
            [InlineKeyboardButton("🎵 Download Track", callback_data='download_info')],
            [
                InlineKeyboardButton("🚀 Join BotLand AI", url="https://t.me/botlandai"),
                InlineKeyboardButton("📱 Join TechBlog LK", url="https://t.me/techbloglk")
            ],
            [InlineKeyboardButton("👨‍💻 Contact Owner", url="https://t.me/hdjhhhhs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "🎧 *Welcome to Spotify Track Info Bot\\!*\n\n"
            "✨ I can help you get information and download links for Spotify tracks\\.\n"
            "🔽 Click the buttons below to get started\\!",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    elif query.data == 'download_info':
        keyboard = [
            [InlineKeyboardButton("🔍 How to Use", callback_data='help')],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "🎵 To download a track, use the /download command followed by the Spotify URL\n"
            "Example: `/download https://open\\.spotify\\.com/track/\\.\\.\\.`",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    elif query.data.startswith('get_link_'):
        # Extract track ID from callback data
        track_id = query.data.replace('get_link_', '')
        # Reconstruct full URL
        track_url = f"https://open.spotify.com/track/{track_id}"
        
        status_message = await query.message.reply_text("🔄 Downloading track... Please wait, this may take a moment.")
        
        # Get the download URL
        download_url = download_track(track_url)
        
        if download_url:
            # Get track metadata for filename
            track_data = get_spotify_track_metadata(track_url)
            if not track_data:
                await status_message.edit_text("❌ Failed to get track information.")
                return
                
            # Create a meaningful filename
            filename = f"{track_data['name']} - {track_data['artist']}"
            
            try:
                # Download the file to server
                await status_message.edit_text("⬇️ File found! Downloading to server...")
                
                # Create downloads directory if it doesn't exist
                if not os.path.exists("downloads"):
                    os.makedirs("downloads")
                
                # Clean filename of invalid characters
                clean_filename = "".join(c for c in filename if c.isalnum() or c in " -_").strip()
                filepath = os.path.join("downloads", f"{clean_filename}.mp3")
                
                # Download the file
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Send the file to user
                await status_message.edit_text("📤 Sending file to you now...")
                
                with open(filepath, 'rb') as audio_file:
                    caption = (
                        f"🎵 *{track_data['name']}*\n"
                        f"👤 Artist: {track_data['artist']}\n"
                        f"💿 Album: {track_data['album_name']}"
                    )
                    
                    await query.message.reply_audio(
                        audio=audio_file,
                        title=track_data['name'],
                        performer=track_data['artist'],
                        caption=caption,
                        parse_mode='Markdown'
                    )
                
                # Delete status message and temporary file
                await status_message.delete()
                
                # Optional: Delete the file to save space
                # os.remove(filepath)
                
                # Send a follow-up message with menu button
                keyboard = [[InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(
                    "✅ Enjoy your music! Want to download another track?",
                    reply_markup=reply_markup
                )
                
            except Exception as e:
                print(f"Error downloading/sending file: {str(e)}")
                keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data=f'get_link_{track_id}')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await status_message.edit_text(
                    "❌ Failed to download the track\\. Please try again\\.",
                    reply_markup=reply_markup,
                    parse_mode='MarkdownV2'
                )
        else:
            keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data=f'get_link_{track_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await status_message.edit_text(
                "❌ Failed to get download link\\. Please try again\\.",
                reply_markup=reply_markup,
                parse_mode='MarkdownV2'
            )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "open.spotify.com/track/" in update.message.text:
        await process_spotify_url(update, update.message.text)
    else:
        keyboard = [
            [InlineKeyboardButton("🔍 How to Use", callback_data='help')],
            [InlineKeyboardButton("🎵 Download Track", callback_data='download_info')],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ Please send a valid Spotify track URL or use the /download command\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    
    # Check if the error is from a callback query
    if update.callback_query:
        await update.callback_query.message.reply_text(
            "⚠️ Sorry, something went wrong\\. Please try again later\\.",
            parse_mode='MarkdownV2'
        )
    elif update.message:
        await update.message.reply_text(
            "⚠️ Sorry, something went wrong\\. Please try again later\\.",
            parse_mode='MarkdownV2'
        )

def main():
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('download', download_command))
    
    # Callback queries
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    # Error handler
    app.add_error_handler(error)
    
    print("Bot is running...")
    app.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()
