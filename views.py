import discord
from database import Session, UserInterest

class PostingView(discord.ui.View):
    def __init__(self, posting_id):
        super().__init__(timeout=None)
        self.add_item(ApplicationStatusSelect(posting_id))
        self.posting_id = posting_id

    def already_exists(self, session, post_id, user_id):
        return session.query(UserInterest).filter_by(
        user_id=user_id,
        posting_id=post_id
        ).first()

    @discord.ui.button(label="Interested", style=discord.ButtonStyle.green)
    async def interested_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # what should happen here?
        # hint: you'll want to open a Session, find-or-create a UserInterest row
        # for (interaction.user.id, self.posting_id), set status="interested",
        # commit, then reply to the interaction

        session = Session()

        exists = self.already_exists(session, self.posting_id, str(interaction.user.id))

        if exists:
            exists.status = "interested"
        else:
            new_interest = UserInterest(
            user_id=str(interaction.user.id),
            posting_id=self.posting_id,
            status="interested"
            )

            session.add(new_interest)

        session.commit()
        
        session.close()

        await interaction.response.send_message("Set status to Interested!", ephemeral=True)

    @discord.ui.button(label="Not Interested", style=discord.ButtonStyle.red)
    async def not_interested_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = Session()

        exists = self.already_exists(session, self.posting_id, str(interaction.user.id))
        if exists:
            exists.status = "not_interested"
        else:
            new_interest = UserInterest(
                user_id=str(interaction.user.id),
                posting_id=self.posting_id,
                status="not_interested"
            )
            session.add(new_interest)
        session.commit()
        session.close()

        await interaction.response.send_message("Set status to Not Interested!", ephemeral=True)


class ApplicationStatusSelect(discord.ui.Select):
    def __init__(self, posting_id):
        options = [
            discord.SelectOption(label="Not Started", value="not_started"),
            discord.SelectOption(label="In Progress", value="in_progress"),
            discord.SelectOption(label="Waiting", value="waiting"),
            discord.SelectOption(label="Received", value="received")
        ]
        super().__init__(placeholder="Set your application status...", options=options, min_values=1, max_values=1)
        self.posting_id = posting_id

    async def callback(self, interaction: discord.Interaction):
        chosen_status = self.values[0]
        # your turn: upsert Application AND upsert UserInterest here
        ...

        